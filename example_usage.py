#!/usr/bin/env python3
"""
Example usage of MahjongQuestionGenerator with and without MCP tools.
"""

import logging

from generator.generator import MahjongQuestionGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_without_mcp():
    """Example of using MahjongQuestionGenerator without MCP tools."""
    print("\n=== Example without MCP tools ===")

    # Create a mock model for demonstration
    class MockModel:
        def __init__(self):
            self.model = "mock-model"

        def invoke(self, data):
            # Return a mock response that looks like a valid Hand JSON
            return """{
                "tiles": ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1z", "1z", "1z"],
                "win_tile": "1p",
                "melds": [],
                "dora_indicators": ["2m"],
                "is_riichi": true,
                "is_tsumo": false,
                "is_ippatsu": false,
                "is_rinshan": false,
                "is_chankan": false,
                "is_haitei": false,
                "is_houtei": false,
                "is_daburu_riichi": false,
                "is_nagashi_mangan": false,
                "is_tenhou": false,
                "is_chiihou": false,
                "is_renhou": false,
                "is_open_riichi": false,
                "player_wind": "east",
                "round_wind": "east"
            }"""

    try:
        # Create generator without MCP
        generator = MahjongQuestionGenerator(MockModel(), use_mcp=False)
        print("✓ Generator created successfully (without MCP)")

        # Generate a question
        query = "リーチをかけて自摸で和了した場合の点数計算問題を作成してください"
        result = generator.generate_question(query)

        print("✓ Question generated successfully")
        print(
            f"Sample result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

    except Exception as e:
        print(f"✗ Error: {e}")


def example_with_mcp():
    """Example of using MahjongQuestionGenerator with MCP tools."""
    print("\n=== Example with MCP tools ===")

    try:
        from langchain_community.llms.fake import FakeListLLM
        
        # Create a fake LLM for demonstration
        llm = FakeListLLM(responses=["Test response"])
        
        # Create generator with MCP tools enabled
        generator = MahjongQuestionGenerator(llm, use_mcp=True)
        print("✓ MCP generator created successfully")
        print(f"✓ MCP enabled: {generator.use_mcp}")
        print(f"✓ Available tools: {[tool.name for tool in generator.tools]}")
        print(f"✓ Agent executor available: {generator.agent_executor is not None}")
        
        # In real usage with a proper LLM:
        print("\nFor real usage:")
        print("1. Use a real LLM like ChatAnthropic or ChatOpenAI")
        print("2. The LLM will automatically use MCP tools to verify generated questions")
        print("3. Tools available: calculate_mahjong_score, validate_mahjong_hand, check_winning_hand")

    except ImportError as e:
        print(f"✗ Error: {e}")




if __name__ == "__main__":
    print("MahjongQuestionGenerator Usage Examples")
    print("=" * 50)

    example_without_mcp()
    example_with_mcp()

    print("\n=== Available Approaches ===")
    print("1. Basic Generation (MahjongQuestionGenerator with use_mcp=False):")
    print("   - Simple question generation without verification")
    print("   - Fast and lightweight")
    
    print("\n2. MCP Tools (MahjongQuestionGenerator with use_mcp=True):")
    print("   - LLM can use mahjong calculation tools during generation")
    print("   - Automatic verification of generated questions")
    print("   - ReAct agent with specialized mahjong tools")
    
    print("\n=== Available MCP Tools ===")
    print("- calculate_mahjong_score: Full scoring calculation")
    print("- validate_mahjong_hand: Hand validation")
    print("- check_winning_hand: Winning hand verification")
