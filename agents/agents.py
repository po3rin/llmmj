import asyncio
import logging
import os
from datetime import datetime
from typing import AsyncGenerator

from google.adk.agents import Agent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types  # For creating message Content/Parts
from pydantic import BaseModel, Field

from llmmj.llmmj import calculate_score_with_json
from tools.calculation import calculate_mahjong_score  # check_hand_validity,
from tools.calculation import final_output_message_check

MODEL = "gemini-2.5-flash"


rule_path = os.path.join(os.path.dirname(__file__), "../sources/rule_en.md")
with open(rule_path, "r") as f:
    rule_str = f.read()
cot_path = os.path.join(os.path.dirname(__file__), "../sources/cot_en.md")
with open(cot_path, "r") as f:
    cot_str = f.read()


async def create_session(
    app_name: str, user_id: str, session_id: str
) -> InMemorySessionService:
    session_service_stateful = InMemorySessionService()
    print("✅ New InMemorySessionService created for state demonstration.")

    # Define initial state data - user prefers Celsius initially
    initial_state = {}

    # Create the session, providing the initial state
    session_stateful = await session_service_stateful.create_session(
        app_name=app_name,  # Use the consistent app name
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )

    return session_service_stateful


def get_mahjong_score_question_generator_agent() -> Agent:
    mahjong_score_question_generator_agent = Agent(
        model=MODEL,
        name="mahjong_score_question_generator_agent",
        description="Sub-Agent: This agent is responsible for generating mahjong score calculation problem.",
        instruction="""
        Read state['current_score'] (if exists) and generate a mahjong score calculation problem.
        
        ## Steps
        1. Generate a mahjong score calculation problem
        2. Return the mahjong score calculation problem.

        ## Acknowledgement
        ### Mahjong Rules
        """
        + rule_str
        + """
        
        ## Tile Notation
        Mahjong hands are represented in 136 format. Man tiles are denoted by m, pin tiles by p, sou tiles by s, and honor tiles by z. Each tile has 4 copies.
        1-man:1m, 2-man:2m, 3-man:3m, 4-man:4m, 5-man:5m, 6-man:6m, 7-man:7m, 8-man:8m, 9-man:9m
        1-pin:1p, 2-pin:2p, 3-pin:3p, 4-pin:4p, 5-pin:5p, 6-pin:6p, 7-pin:7p, 8-pin:8p, 9-pin:9p
        1-sou:1s, 2-sou:2s, 3-sou:3s, 4-sou:4s, 5-sou:5s, 6-sou:6s, 7-sou:7s, 8-sou:8s, 9-sou:9s
        East:1z, South:2z, West:3z, North:4z, White:5z, Green:6z, Red:7z
        
        ## Requirements
        - reach info is required.
        
        ## Advices
        - When the required fu is large, a kan is often required.

        ### Chain of Thought Example
        """
        + cot_str
        + """
        """,
        output_key="candidate_mahjong_score_calculation_problem",
    )
    print(f"✅ Agent '{mahjong_score_question_generator_agent.name}' redefined.")
    return mahjong_score_question_generator_agent


def get_mahjong_score_question_checker_agent() -> Agent:
    mahjong_score_question_checker_agent = Agent(
        model=MODEL,
        name="mahjong_score_question_checker_agent",
        description="Sub-Agent: This agent is responsible for checking the validity of the mahjong score calculation problem.",
        instruction="""
        Handles mahjong score question checking using the 'calculate_mahjong_score' tool. 
        
        ## Steps
        1. Receive the mahjong score calculation problem.
        2. You Must check the validity of the mahjong score calculation problem using the 'calculate_mahjong_score' tool.
        3. Return check result.
        
        ## Tools
        - calculate_mahjong_score: Calculate the mahjong score.
        """,
        tools=[calculate_mahjong_score],
        output_key="mahjong_score_calculation_problem_check_result",
    )
    print(f"✅ Agent '{mahjong_score_question_checker_agent.name}' redefined.")
    return mahjong_score_question_checker_agent


def get_mahjong_supervisor_agent() -> Agent:
    root_agent_stateful = Agent(
        name="mahjong_supervisor_agent",
        model=MODEL,
        description="Main supervisor agent: This agent is responsible for managing the collaboration between the mahjong score calculation problem generation agent and the agent that creates the final output message.",
        instruction="""
        Read state['current_score'] (if exists) and generate a mahjong score calculation problem with agent (mahjong_score_question_generator_agent) and agent (mahjong_score_question_checker_agent).
        
        ## Steps
        1. You Must request the mahjong score calculation problem with agent (mahjong_score_question_generator_agent).
        2. You Must check the validity of the mahjong score calculation problem. and match user instruction(han & fu) with agent (mahjong_score_question_checker_agent).
        3. If the mahjong score calculation problem is invalid or not match user instruction, return step1. Tell mahjong_score_question_generator_agent what went wrong and ask them to fix the problem.
        
        ## Sub-Agents
        - mahjong_score_question_generator_agent: This agent is responsible for generating mahjong problems.
        - mahjong_score_question_checker_agent: This agent is responsible for checking the validity of the mahjong score calculation problem.

        ## Requirements
        ### 1: Mahjong score calculation problem must be generated by mahjong_score_question_generator_agent.
        ### 2: Mahjong score calculation problem must be checked by mahjong_score_question_checker_agent.
        """,
        sub_agents=[
            get_mahjong_score_question_generator_agent(),
            get_mahjong_score_question_checker_agent(),
        ],
        output_key="last_final_score_calculation_problem",
    )
    print(
        f"✅ Root Agent '{root_agent_stateful.name}' created using stateful tool and output_key."
    )
    return root_agent_stateful


def get_final_output_json_generator_agent() -> Agent:
    final_output_json_generator_agent = Agent(
        model=MODEL,
        name="final_output_json_generator_agent",
        description="Sub-Agent: This agent is responsible for generating the final output message for user.",
        instruction="""You are responsible for returning a string to the user that can be loaded directly using python's json.load without adding markdown JSON tags. Please make sure to check that the JSON contains the required keys using the final_output_message_check tool. Do nothing else.
        
        ## Steps
        1. Receive the mahjong score calculation problem.
        2. Format message string to JSON string has the required keys.
        3. Finally, You must check the validity of the JSON string using the 'final_output_message_check' tool. if the JSON string is invalid, return step1.
        4. Return JSON string only (no markdown JSON tags).
        
        ## Tools
        - final_output_message_check: check the final output message is valid.

        ## Required JSON Format
        - The message must be in the following JSON format:
            {
                "tiles": list[str],
                "melds": list[MeldInfo],
                "win_tile": str,
                "dora_indicators": list[str],
                "is_riichi": bool,
                "is_tsumo": bool,
                "player_wind": str,
                "round_wind": str
            }
        - tiles: list[str]: Array in 136 format representing the winning hand. Important: Must include all tiles in the hand, including those specified in melds. Example: For a hand with 10 tiles + 4 ankan tiles + 1 winning tile, specify all 15 tiles like tiles=['1m', '2m', '3m', '4m', '4m', '5p', '5p', '5p', '7p', '8p', '1z', '1z', '1z', '1z', '1s'].
        - melds: list[MeldInfo]: Meld information. MeldInfo format only: [{"tiles": ["1z", "1z", "1z", "1z"], "is_open": false}]
            - tiles: Meld tiles (136 format). These tiles must also be included in the tiles field.
            - is_open: true=open meld (minkan, pon, chi), false=closed meld (ankan)
        - win_tile (str): The winning tile
        - dora_indicators (list[str]): Dora indicator tiles
        - is_riichi (bool): Whether riichi is declared. Cannot declare riichi after calling melds, so must be False if melds is not None.
        - is_tsumo (bool): Whether it's a tsumo win
        - player_wind (str): Player's wind (east, south, west, north)
        - round_wind (str): Round wind (east, south, west, north)
        """,
        tools=[final_output_message_check],
        output_key="last_final_output_message",
    )
    print(f"✅ Agent '{final_output_json_generator_agent.name}' redefined.")
    return final_output_json_generator_agent


class CheckStatusAndEscalate(BaseAgent):
    expected_han: int = Field(..., description="Expected han")
    expected_fu: int = Field(..., description="Expected fu")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        print(f"🔍 CheckStatusAndEscalate: {self.expected_han}, {self.expected_fu}")
        status = "fail"
        output = ctx.session.state.get("last_final_output_message", None)
        if output is None:
            print("No final output message found in session state")
            raise Exception("No final output message found in session state")

        score_response = calculate_score_with_json(output)

        if (
            score_response.han == self.expected_han
            and score_response.fu == self.expected_fu
        ):
            print(
                f"✅ CheckStatusAndEscalate: got: {score_response.han}, {score_response.fu} == want: {self.expected_han}, {self.expected_fu}"
            )
            status = "pass"
        else:
            print(
                f"❌ CheckStatusAndEscalate: got: {score_response.han}, {score_response.fu} != want: {self.expected_han}, {self.expected_fu}"
            )
            status = "fail"

        ctx.session.state["current_score"] = score_response

        should_stop = status == "pass"
        yield Event(author=self.name, actions=EventActions(escalate=should_stop))


async def call_agent_async(query: str, runner, user_id, session_id) -> str:
    """Sends a query to the agent and prints the final response."""
    agent_logger = logging.getLogger("agent_interactions")
    # Log session start info
    agent_logger.info(
        f"SESSION[{session_id}] ========== NEW INTERACTION START =========="
    )

    query_msg = f">>> User Query: {query}"
    agent_logger.info(f"SESSION[{session_id}] USER[{user_id}] {query_msg}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # # Show all events during execution including thinking process and sub-agent conversations
        # if event.content and event.content.parts:
        #     parts_text = "\n".join([part.text for part in event.content.parts if hasattr(part, 'text') and part.text])
        #     if parts_text:
        #         event_msg = f"[{event.author}]: {parts_text}"
        #         # print(f"\n{event_msg}")
        #         agent_logger.info(f"SESSION[{session_id}] {event_msg}")

        # # Also show tool calls if any
        # if hasattr(event, 'actions') and event.actions and hasattr(event.actions, 'tool_calls'):
        #     for tool_call in event.actions.tool_calls:
        #         tool_msg = f"[{event.author}] Tool Call: {tool_call.name}"
        #         # print(f"\n{tool_msg}")
        #         agent_logger.info(f"SESSION[{session_id}] {tool_msg}")
        #         if hasattr(tool_call, 'parameters'):
        #             param_msg = f"  Parameters: {tool_call.parameters}"
        #             # print(param_msg)
        #             agent_logger.info(f"SESSION[{session_id}] {param_msg}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
                final_msg = f">>> Final Response: {final_response_text}"
                agent_logger.info(f"SESSION[{session_id}] Final Response:\n{final_msg}")
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
                escalate_msg = f">>> Agent Escalated: {final_response_text}"
                agent_logger.info(
                    f"SESSION[{session_id}] Final Response:\n{escalate_msg}"
                )

    # Log session end info
    agent_logger.info(f"SESSION[{session_id}] ========== INTERACTION END ==========")

    return final_response_text


async def get_sequential_runner(app_name: str, user_id: str, session_id: str) -> Runner:
    # Create runner for each query to avoid session conflicts
    session_service = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    supervisor_agent = get_mahjong_supervisor_agent()
    final_output_json_generator_agent = get_final_output_json_generator_agent()

    root_agent = SequentialAgent(
        name="mahjong_sequential_agent",
        sub_agents=[supervisor_agent, final_output_json_generator_agent],
    )

    return Runner(agent=root_agent, app_name=app_name, session_service=session_service)


async def get_loop_runner(
    app_name: str, user_id: str, session_id: str, expected_han: int, expected_fu: int
) -> Runner:
    session_service = await create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    supervisor_agent = get_mahjong_supervisor_agent()
    final_output_json_generator_agent = get_final_output_json_generator_agent()

    sequential_agent = SequentialAgent(
        name="mahjong_sequential_agent",
        sub_agents=[supervisor_agent, final_output_json_generator_agent],
    )

    root_agent = LoopAgent(
        name="mahjong_loop_agent",
        max_iterations=5,
        sub_agents=[
            sequential_agent,
            CheckStatusAndEscalate(
                name="StopChecker", expected_han=expected_han, expected_fu=expected_fu
            ),
        ],
    )

    return Runner(agent=root_agent, app_name=app_name, session_service=session_service)


async def run(runner: Runner, user_id: str, session_id: str, query: str) -> str:
    return await call_agent_async(
        query=query,
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )
