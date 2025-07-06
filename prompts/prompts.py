from .parts import cot_str, required_json_format_str, rule_str, tile_notation_str

generate_question_prompt_template = (
    """
You are an expert in creating Japanese Riichi Mahjong scoring problems.

## Background Knowledge
"""
    + tile_notation_str
    + """

"""
    + required_json_format_str
    + """

## Instructions
{query}
"""
)

generate_question_with_cot_and_rule_prompt_template = (
    """
You are an expert in creating Japanese Riichi Mahjong scoring problems.

## Background Knowledge
"""
    + tile_notation_str
    + """

### Calculation Rules
"""
    + rule_str
    + """

"""
    + cot_str
    + """

"""
    + required_json_format_str
    + """

## Instructions
{query}
"""
)


generate_question_with_tools_prompt_template = (
    """
You are an expert in creating Japanese Riichi Mahjong scoring problems. 

## ** Required Steps **
1. Generate a problem.
2. Use the calculate_mahjong_score tool to verify that the parameters are correct and that the calculation result of the problem matches the specified answer.
3. Return the problem and the answer.
4. If the parameters are incorrect or the calculation result does not match the specified answer, repeat the process from step 1.

## Background Knowledge
"""
    + tile_notation_str
    + """

### Calculation Rules
"""
    + rule_str
    + """

### Example of thinking steps
"""
    + cot_str
    + """

"""
    + required_json_format_str
    + """

### Tool Description
- calculate_mahjong_score: Calculates mahjong scores. From information such as hand tiles, winning tile, melds, dora etc., it calculates han, fu, and points, and also returns details of the yaku.

## Instructions
{query}
"""
)
