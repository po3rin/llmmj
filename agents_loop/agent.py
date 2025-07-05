import logging
from typing import Any, Dict

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools import ToolContext

from llmmj.llmmj import calculate_score_with_json
from prompts.parts import cot_str, required_json_format_str, rule_str, tile_notation_str
from tools.calculation import calculate_mahjong_score

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def exit_loop(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Call this function ONLY when code validation has completed successfully,
    signaling the iterative process should end.

    Args:
        tool_context: Context for tool execution

    Returns:
        Empty dictionary
    """
    logger.info("----------- EXIT LOOP TRIGGERED -----------")
    logger.info("Code validation completed successfully")
    logger.info("Loop will exit now")
    logger.info("------------------------------------------")

    tool_context.actions.escalate = True
    return {}


mahjong_score_question_generator_agent = Agent(
    model=MODEL,
    name="mahjong_score_question_generator_agent",
    description="Sub-Agent: This agent is responsible for generating mahjong score calculation question.",
    instruction="""
    generate a mahjong score calculation question.

    ## Acknowledgement
    ### Mahjong Rules
    """
    + rule_str
    + tile_notation_str
    + """
    
    ## Requirements
    - reach info is required.
    
    ## Advices
    - When the required fu is large, a kan is often required.

    ### Chain of Thought Example
    """
    + cot_str
    + """
    """,
    output_key="current_question",
)


validation_agent = Agent(
    model=MODEL,
    name="validation_agent",
    description="This agent is responsible for checking the validity of mahjong score calculation problems, using 'calculate_mahjong_score' tool to ensure that the problem matches the answer given by the user.",
    instruction="""
    Check the validity of the mahjong score calculation question using 'calculate_mahjong_score' tool to ensure that the problem matches the answer given by the user.
    
    ## **Current Question**
    {current_question}
    
    ## Tools
    - calculate_mahjong_score: Calculate the mahjong score.
    
    ## Core Rules
    - You must use the 'calculate_mahjong_score' tool to check the validity of the mahjong score calculation question.
    - If the mahjong score calculation question is invalid, you must return the error message.
    - If the answer given by the 'calculate_mahjong_score' tool is different from the one the user specified, you must return the tool's response.
    
    ## OUTPUT INSTRUCTIONS
    **Scenario 1: Validation Failed (Error Response)**
    If the `calculate_mahjong_score` function's output (specifically from `stderr`) contains any error messages:
    - Extract and output *only* the content from the `stderr` stream of the validation tool.
    - Do NOT add any extra formatting, explanations, or commentary to the `stderr` output.
    - The output should be the raw error message(s) provided by the `calculate_mahjong_score` tool.

    **Scenario 2: Validation Failed (The answer is different from the user's instructions)**
    If the `calculate_mahjong_score` function's output is not match with user instruction(han & fu),
    - Extract and output *only* the entire response of the 'calculate_mahjong_score' tool.
    - You can format the output as a meaningful message to the Agent responsible for making the fix.

    **Scenario 3: Validation Succeeds**
    If the `calculate_mahjong_score` function's output is same with user instruction(han & fu),
    - Call the `exit_loop` function.
    - Then, return the precise string: "Validation succeeded. Exiting the refinement loop."
    - Do NOT output anything else.
    """,
    tools=[calculate_mahjong_score, exit_loop],
    output_key="validation_errors",
)


refining_agent = Agent(
    model=MODEL,
    name="refining_agent",
    description="Sub-Agent: This agent is responsible for refining the mahjong score calculation question.",
    instruction="""
    Refine the mahjong score calculation question.
    
    ## **Current Question**
    {current_question}
    
    **Errors to Fix (from Validation Agent):**
    validation_errors:
    {validation_errors}
    (This is a list of specific error messages indicating issues in the Current Question.)
    
    ## Core Rules
    - If exists validation_errors, you must refine the mahjong score calculation question.
    - You must return the refined mahjong score calculation question.
    
    ### Mahjong Rules
    """
    + rule_str,
    output_key="current_question",
)


output_json_formatter_agent = Agent(
    model=MODEL,
    name="output_json_formatter_agent",
    description="Sub-Agent: This agent is responsible for formatting the output json string.",
    instruction="""
    Format mahjong score calculation question to output json string.
    
    ## Steps
    1. Receive the current mahjong score calculation question.
    2. Format message string to JSON string has the required keys.
    3. Return JSON string only (**no markdown JSON tags**).

    """
    + required_json_format_str,
    output_key="current_output_json",
)


output_json_validation_agent = Agent(
    model=MODEL,
    name="output_json_validation_agent",
    description="Sub-Agent: This agent is responsible for checking the validity of the output json string.",
    instruction="""
    Check the validity of the output json string.
    
    ## **Current Output JSON String**
    {current_output_json}
    
    ## **Tools**
    - calculate_score_with_json: Calculate the mahjong score.
    - exit_loop: Exit the loop.
    
    ## OUTPUT INSTRUCTIONS
    **Scenario 1: Validation Failed (Error)**
    If the `calculate_score_with_json` function's output (specifically from `stderr`) contains any error messages:
    - Extract and output *only* the content from the `stderr` stream of the validation tool.
    - Do NOT add any extra formatting, explanations, or commentary to the `stderr` output.
    - The output should be the raw error message(s) provided by the `calculate_score_with_json` tool.

    **Scenario 2: Validation Succeeds**
    If the `calculate_score_with_json` function's output no error,
    - Call the `exit_loop` function.
    - Then, return the precise string: "Validation succeeded. Exiting the refinement loop."
    - Do NOT output anything else.
    """,
    tools=[calculate_score_with_json, exit_loop],
    output_key="output_json_validation_errors",
)


output_json_refining_agent = Agent(
    model=MODEL,
    name="output_json_refining_agent",
    description="Sub-Agent: This agent is responsible for refining the output json string.",
    instruction="""
    Refine the output json string for the mahjong score calculation question.
    
    ## **Current Output JSON String**
    {current_output_json}
    
    ## **Errors to Fix (from Validation Agent)** 
    output_json_validation_errors:
    {output_json_validation_errors}
    (This is a list of specific error messages indicating issues in the Current Output JSON String.)
    
    """
    + required_json_format_str,
    output_key="current_output_json",
)


candidate_loop_agent = LoopAgent(
    name="candidate_loop_agent",
    description="This agent is responsible for managing the collaboration between the refining agent and the validation agent.",
    max_iterations=8,
    sub_agents=[
        validation_agent,
        refining_agent,
    ],
)

output_candidate_loop_agent = LoopAgent(
    name="output_candidate_loop_agent",
    description="This agent is responsible for managing the collaboration between the output json formatter agent and the output json validation agent.",
    max_iterations=8,
    sub_agents=[output_json_validation_agent, output_json_refining_agent],
)

mahjong_loop_agent = SequentialAgent(
    name="mahjong_loop_agent",
    description="This agent is responsible for managing the collaboration between the candidate loop agent and the output candidate loop agent.",
    sub_agents=[
        mahjong_score_question_generator_agent,
        candidate_loop_agent,
        output_json_formatter_agent,
        output_candidate_loop_agent,
    ],
)


root_agent = mahjong_loop_agent
