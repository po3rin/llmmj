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
    logger.debug("----------- EXIT LOOP TRIGGERED -----------")
    logger.debug("Code validation completed successfully")
    logger.debug("Loop will exit now")
    logger.debug("------------------------------------------")

    tool_context.actions.escalate = True
    return {}


mahjong_score_question_generator_agent = Agent(
    model=MODEL,
    name="mahjong_score_question_generator_agent",
    description="Sub-Agent: This agent is responsible for generating mahjong score calculation question.",
    instruction="""
    Generate a mahjong score calculation problem that results in the specified han and fu.

    ## User Requirements
    The user has specified the target han and fu values. You MUST generate a problem that exactly matches these values.

    ## Acknowledgement
    ### Mahjong Rules
    """
    + rule_str
    + tile_notation_str
    + """
    
    ## Critical Requirements
    - The generated problem MUST result in exactly the han and fu specified by the user
    - Riichi info is REQUIRED (set is_riichi appropriately)
    - Always verify tile counts (max 4 of each tile)
    - Include dora_indicators to achieve the required han
    
    ## Key Constraints
    - Cannot riichi with open melds (if melds exist, is_riichi must be false)
    - Closed hand ron adds 10 fu (menzen ron)
    - Tsumo always adds 2 fu
    - Fu is rounded UP to nearest 10 (e.g., 32→40, 44→50)
    - Some combinations are impossible (e.g., 1 han 20 fu is impossible due to minimum fu rules)
    
    ## Fu Calculation Tips
    - Base fu: 20
    - Yakuhai (dragon/wind) triplet: 8 fu (closed), 4 fu (open)
    - Terminal/honor triplet: 8 fu (closed), 4 fu (open)  
    - Simple triplet (2-8): 4 fu (closed), 2 fu (open)
    - Yakuhai pair: 2 fu (if it's seat/round wind)
    - Tanki (pair wait): 2 fu
    - Kanchan/Penchan wait: 2 fu
    - Closed quad: 16 fu (terminal/honor), 8 fu (simple)
    - Open quad: 8 fu (terminal/honor), 4 fu (simple)
    - Menzen ron (closed hand ron): 10 fu
    - Tsumo: 2 fu (except pinfu)
    
    ## Strategy for Different Fu Targets
    - 25 fu: Chiitoitsu (seven pairs) - always 25 fu
    - 30 fu: Basic closed hand with ryanmen wait
    - 40 fu: Add one simple ankou or special wait
    - 50 fu: Add terminal/honor ankou or multiple fu elements
    - 60+ fu: Usually needs multiple ankou or kan
    - 70+ fu: Often requires kan (especially closed kan)

    ### Chain of Thought Example
    """
    + cot_str,
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
    
    ## **Target Answer (User Specified)**
    Extract the target han and fu from the user's original request. The problem MUST result in exactly these values.
    
    ## Tools
    - calculate_mahjong_score: Calculate the mahjong score.
    - exit_loop: Signal successful validation.
    
    ## Core Validation Rules
    1. You MUST use the 'calculate_mahjong_score' tool to check the validity
    2. Compare the calculated han/fu with the user's specified target values
    3. The calculated values MUST exactly match the target (not just close)
    
    ## OUTPUT INSTRUCTIONS - CRITICAL: MUST FOLLOW EXACTLY
    
    **STEP 1: Always use the calculate_mahjong_score tool first**
    You MUST call calculate_mahjong_score before doing anything else.
    
    **STEP 2: Check the result and follow the appropriate scenario**
    
    **Scenario A: Tool Returns Error (stderr has content)**
    If calculate_mahjong_score has any error in stderr:
    - Output the error message from stderr
    - Add fixing suggestions:
      - "Invalid tile count" → Check for duplicate tiles exceeding 4
      - "Invalid meld" → Verify meld tiles are included in hand tiles
      - "Invalid hand" → Ensure exactly 14 tiles (or 13 + win_tile)
    - DO NOT call exit_loop

    **Scenario B: Tool Succeeds BUT Han/Fu Mismatch**
    If tool runs successfully but calculated han/fu ≠ target han/fu:
    - Output: "Mismatch"
    - Include the full calculation details
    - Add specific fix suggestions
    - DO NOT call exit_loop

    **Scenario C: PERFECT MATCH - Tool Succeeds AND Han/Fu Match**
    If tool succeeds AND calculated han/fu exactly equals target han/fu:
    - IMMEDIATELY call the exit_loop tool (this is MANDATORY)
    - After calling exit_loop, output: "Validation succeeded. Exiting the refinement loop."
    - Do NOT output anything else
    
    **CRITICAL**: You MUST call exit_loop when validation succeeds, otherwise the loop will continue forever!
    """,
    tools=[calculate_mahjong_score, exit_loop],
    output_key="validation_errors",
)


refining_agent = Agent(
    model=MODEL,
    name="refining_agent",
    description="Sub-Agent: This agent is responsible for refining the mahjong score calculation question.",
    instruction="""
    Refine the mahjong score calculation question based on validation errors.
    
    ## **Current Question**
    {current_question}
    
    ## **Validation Errors**
    {validation_errors}
    
    ## Refinement Strategy
    Based on the error type, apply these fixes:
    
    ### For Han/Fu Mismatch:
    1. **Han Adjustment**:
       - Too few han: Add dora indicators or enable yaku (riichi, tanyao, etc.)
       - Too many han: Remove dora or disable yaku
       - Remember: Each dora indicator adds 1 han per matching tile
    
    2. **Fu Adjustment**:
       - Too few fu: 
         * Add closed triplets (ankou)
         * Change to tanki/kanchan/penchan wait (+2 fu)
         * Add terminal/honor triplets (+8 fu closed)
         * Consider adding kan
       - Too much fu:
         * Remove or open triplets
         * Change to ryanmen wait (0 fu)
         * Replace terminal/honor with simple tiles
       - Remember: Fu rounds UP to nearest 10
    
    ### For Tile Count Errors:
    - Count each tile type (max 4 of each)
    - Ensure tiles in melds are included in main tiles array
    - Verify exactly 14 tiles total (or appropriate with kan)
    
    ### For Rule Violations:
    - Cannot riichi with open melds
    - Chiitoitsu is always 25 fu
    - Pinfu requirements: all sequences, ryanmen wait, no yakuhai pair
    
    ## Output Requirements
    - Return a complete refined problem description
    - Ensure all tile counts are valid
    - Verify the refinement will produce target han/fu
    
    ### Mahjong Rules
    """
    + rule_str
    + tile_notation_str
    + cot_str,
    output_key="current_question",
)


output_json_formatter_agent = Agent(
    model=MODEL,
    name="output_json_formatter_agent",
    description="Sub-Agent: This agent is responsible for formatting the output json string.",
    instruction="""
    Convert the mahjong score calculation question into a valid JSON string following the exact schema.
    
    ## Current Question
    {current_question}
    
    ## Conversion Steps
    1. Extract all tile information from the problem description
    2. Identify melds (pon, chii, kan) and format them correctly
    3. Map all fields to the required JSON schema
    4. Validate data types for each field
    
    ## Critical Rules
    - Output ONLY the JSON string - no markdown formatting, no ```json tags
    - All tiles must be in 136 format (e.g., "1m", "2p", "3s", "1z")
    - Melds must include ALL their tiles in the main tiles array
    - Boolean values must be lowercase (true/false, not True/False)
    - Wind directions must be lowercase: "east", "south", "west", "north"
    - Empty arrays should be [] not null
    - Missing optional fields should be omitted or set to appropriate defaults
    
    ## Common Mappings
    - "riichi declared" → "is_riichi": true
    - "tsumo win" → "is_tsumo": true
    - "ron" → "is_tsumo": false
    - "closed kan" → "is_open": false
    - "open kan/pon/chii" → "is_open": true
    - Note: Pon and Chii are ALWAYS open (is_open: true), only Kan can be closed

    """
    + required_json_format_str
    + """
    
    ## Example Output Format (DO NOT include backticks):
    {"tiles": ["1m", "2m", "3m", "4m", "4m", "5p", "5p", "5p", "7s", "8s", "9s", "1z", "1z", "2z"], "melds": [], "win_tile": "2z", "dora_indicators": ["3m"], "is_riichi": true, "is_tsumo": false, "player_wind": "east", "round_wind": "east"}
    """,
    output_key="current_output_json",
)


output_json_validation_agent = Agent(
    model=MODEL,
    name="output_json_validation_agent",
    description="Sub-Agent: This agent is responsible for checking the validity of the output json string.",
    instruction="""
    Validate the JSON string for schema compliance and correctness.
    
    ## **Current Output JSON String**
    {current_output_json}
    
    ## **Tools**
    - calculate_score_with_json: Validate JSON by calculating the mahjong score
    - exit_loop: Signal successful validation
    
    ## Validation Checks
    1. **JSON Parse Check**: Ensure the string is valid JSON
    2. **Schema Compliance**: Verify all required fields are present
    3. **Data Type Check**: Confirm correct types (arrays, booleans, strings)
    4. **Tile Format**: All tiles in 136 format (e.g., "1m", not "1-man")
    5. **Meld Consistency**: Tiles in melds must also appear in main tiles array
    6. **Calculation Check**: Use calculate_score_with_json tool
    
    ## Common JSON Errors to Check
    - Missing quotes around strings
    - Uppercase boolean values (should be lowercase)
    - null instead of empty arrays []
    - Missing required fields
    - Invalid tile notation
    - Meld tiles not included in main tiles array
    
    ## OUTPUT INSTRUCTIONS - CRITICAL: MUST FOLLOW EXACTLY
    
    **STEP 1: Always use the calculate_score_with_json tool first**
    You MUST call calculate_score_with_json before doing anything else.
    
    **STEP 2: Check the result and follow the appropriate scenario**
    
    **Scenario A: JSON/Schema Validation Failed**
    If JSON parsing fails or schema is invalid (before even calling the tool):
    - Output: "JSON Error: [specific issue]"
    - Suggest fix: "Fix: [specific correction needed]"
    - Examples:
      - "JSON Error: Boolean 'True' should be lowercase 'true'"
      - "JSON Error: Missing required field 'win_tile'"
      - "JSON Error: Meld tiles ['1z','1z','1z'] not found in main tiles array"
    - DO NOT call exit_loop

    **Scenario B: Tool Returns Error (Calculation Failed)**
    If calculate_score_with_json returns an error in stderr:
    - Extract the specific error from stderr
    - Output: "Calculation Error: [error message]"
    - Add context if helpful
    - DO NOT call exit_loop

    **Scenario C: PERFECT SUCCESS - JSON Valid AND Calculation Succeeds**
    If JSON is perfectly valid AND calculate_score_with_json succeeds with no errors:
    - IMMEDIATELY call the exit_loop tool (this is MANDATORY)
    - After calling exit_loop, output: "Validation succeeded. Exiting the refinement loop."
    - Do NOT output anything else
    
    **CRITICAL**: You MUST call exit_loop when validation succeeds, otherwise the loop will continue forever!
    """,
    tools=[calculate_score_with_json, exit_loop],
    output_key="output_json_validation_errors",
)


output_json_refining_agent = Agent(
    model=MODEL,
    name="output_json_refining_agent",
    description="Sub-Agent: This agent is responsible for refining the output json string.",
    instruction="""
    Fix the JSON string based on validation errors to ensure schema compliance.
    
    ## **Current Output JSON String**
    {current_output_json}
    
    ## **Validation Errors to Fix**
    {output_json_validation_errors}
    
    ## JSON Fixing Strategies
    
    ### For Schema/Format Errors:
    1. **Boolean Case Issues**:
       - Replace: "True" → "true", "False" → "false"
       - Ensure all booleans are lowercase
    
    2. **Missing Required Fields**:
       - Add missing fields with appropriate values
       - Required: tiles, win_tile, is_riichi, is_tsumo
       - Set reasonable defaults if information is missing
    
    3. **Tile Format Issues**:
       - Convert to 136 format: "1-man" → "1m", "East" → "1z"
       - Ensure all tiles use correct notation
    
    4. **Meld Consistency**:
       - If error says meld tiles not in main array, ADD them to tiles array
       - Count tiles carefully (remember: 14 total, or more with kan)
       - Format: {"tiles": ["1z", "1z", "1z"], "is_open": true}
       - Remember: Pon/Chii are always is_open=true, only Kan can be is_open=false
    
    ### For Calculation Errors:
    1. **Invalid Hand Structure**:
       - Ensure exactly 14 tiles (or 13 + win_tile)
       - With kan: add 3 extra tiles per kan
       - Check for duplicate tiles exceeding limit of 4
    
    2. **Invalid Melds**:
       - Pon: exactly 3 identical tiles
       - Kan: exactly 4 identical tiles
       - Chii: 3 consecutive tiles of same suit
    
    ## Output Requirements
    - Return ONLY the corrected JSON string
    - NO markdown formatting or backticks
    - Ensure valid JSON syntax
    - Maintain all data from original that wasn't errored
    
    """
    + required_json_format_str
    + """
    
    ## Example Fix:
    Error: "JSON Error: Boolean 'True' should be lowercase 'true'"
    Original: {"is_riichi": True, ...}
    Fixed: {"is_riichi": true, ...}
    
    Error: "JSON Error: Meld tiles ['1z','1z','1z'] not found in main tiles array"
    Original: {"tiles": ["1m", "2m", ...], "melds": [{"tiles": ["1z", "1z", "1z"], "is_open": true}], ...}
    Fixed: {"tiles": ["1m", "2m", ..., "1z", "1z", "1z"], "melds": [{"tiles": ["1z", "1z", "1z"], "is_open": true}], ...}
    """,
    output_key="current_output_json",
)

candidate_loop_agent = LoopAgent(
    name="candidate_loop_agent",
    description="This agent is responsible for managing the collaboration between the refining agent and the validation agent.",
    max_iterations=5,
    sub_agents=[
        validation_agent,
        refining_agent,
    ],
)

output_candidate_loop_agent = LoopAgent(
    name="output_candidate_loop_agent",
    description="This agent is responsible for managing the collaboration between the output json formatter agent and the output json validation agent.",
    max_iterations=5,
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
