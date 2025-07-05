import logging

from google.adk.runners import Runner
from google.genai import types


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


async def run(runner: Runner, user_id: str, session_id: str, query: str) -> str:
    return await call_agent_async(
        query=query,
        runner=runner,
        user_id=user_id,
        session_id=session_id,
    )
