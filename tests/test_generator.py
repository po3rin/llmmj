import json
import unittest
from unittest.mock import Mock, patch

from entity.entity import Hand
from exceptions import AgentSetupError, JSONParseError
from generator.generator import MahjongQuestionGenerator


class TestMahjongQuestionGenerator(unittest.TestCase):
    def setUp(self):
        """テストの準備"""
        self.mock_model = Mock()
        self.mock_model.model_name = "test_model"
        self.mock_model.model = "test_model"
        
        # テスト用の手牌データ
        self.test_hand_data = {
            "tiles": ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "2p", "2p"],
            "win_tile": "2p",
            "melds": None,
            "dora_indicators": ["1z"],
            "is_riichi": True,
            "is_tsumo": False,
            "player_wind": "east",
            "round_wind": "east"
        }
        
        self.test_hand = Hand(**self.test_hand_data)

    def test_init_simple_mode(self):
        """シンプルモードでの初期化テスト"""
        generator = MahjongQuestionGenerator(self.mock_model, use_tools=False)
        
        self.assertEqual(generator.model, self.mock_model)
        self.assertEqual(generator.model_name, "test_model")
        self.assertFalse(generator.use_tools)
        self.assertEqual(generator.tools, [])
        self.assertIsNone(generator.agent_executor)

    def test_init_tools_mode(self):
        """ツールモードでの初期化テスト"""
        with patch('generator.generator.pull') as mock_pull, \
             patch('generator.generator.create_react_agent') as mock_create_agent, \
             patch('generator.generator.AgentExecutor') as mock_agent_executor:
            
            mock_pull.return_value = Mock()
            mock_create_agent.return_value = Mock()
            mock_agent_executor.return_value = Mock()
            
            generator = MahjongQuestionGenerator(self.mock_model, use_tools=True)
            
            self.assertTrue(generator.use_tools)
            self.assertEqual(len(generator.tools), 1)
            self.assertIsNotNone(generator.agent_executor)

    def test_init_with_custom_template(self):
        """カスタムテンプレートでの初期化テスト"""
        custom_template = "Custom template: {query}"
        generator = MahjongQuestionGenerator(
            self.mock_model, 
            use_tools=False, 
            query_template=custom_template
        )
        
        self.assertEqual(generator.query_template, custom_template)

    def test_generate_question_simple_mode_success(self):
        """シンプルモードでの問題生成成功テスト"""
        generator = MahjongQuestionGenerator(self.mock_model, use_tools=False)
        
        # Mock the chain execution
        with patch('generator.generator.PromptTemplate') as mock_prompt_template:
            mock_prompt = Mock()
            mock_prompt_template.return_value = mock_prompt
            
            # Mock the chain
            mock_chain = Mock()
            mock_chain.invoke.return_value = self.test_hand_data
            mock_prompt.__or__ = Mock(return_value=mock_chain)
            
            result = generator.generate_question("Generate a test question")
            
            self.assertEqual(result, self.test_hand_data)
            mock_chain.invoke.assert_called_once_with({"query": "Generate a test question"})

    def test_generate_question_tools_mode_success(self):
        """ツールモードでの問題生成成功テスト"""
        with patch('generator.generator.pull') as mock_pull, \
             patch('generator.generator.create_react_agent') as mock_create_agent, \
             patch('generator.generator.AgentExecutor') as mock_agent_executor:
            
            mock_pull.return_value = Mock()
            mock_create_agent.return_value = Mock()
            
            # Mock agent executor
            mock_executor = Mock()
            mock_executor.invoke.return_value = {"output": json.dumps(self.test_hand_data)}
            mock_agent_executor.return_value = mock_executor
            
            generator = MahjongQuestionGenerator(self.mock_model, use_tools=True)
            
            result = generator.generate_question("Generate a test question")
            
            self.assertEqual(result, self.test_hand_data)
            mock_executor.invoke.assert_called_once_with({"input": "Generate a test question"})

    def test_generate_question_tools_mode_json_parse_error(self):
        """ツールモードでのJSON解析エラーテスト"""
        with patch('generator.generator.pull') as mock_pull, \
             patch('generator.generator.create_react_agent') as mock_create_agent, \
             patch('generator.generator.AgentExecutor') as mock_agent_executor:
            
            mock_pull.return_value = Mock()
            mock_create_agent.return_value = Mock()
            
            # Mock agent executor with invalid JSON
            mock_executor = Mock()
            mock_executor.invoke.return_value = {"output": "invalid json"}
            mock_agent_executor.return_value = mock_executor
            
            generator = MahjongQuestionGenerator(self.mock_model, use_tools=True)
            
            with self.assertRaises(JSONParseError):
                generator.generate_question("Generate a test question")

    def test_setup_react_failure(self):
        """ReActセットアップ失敗テスト"""
        with patch('generator.generator.pull', side_effect=Exception("Setup failed")):
            with self.assertRaises(AgentSetupError):
                MahjongQuestionGenerator(self.mock_model, use_tools=True)

    def test_model_name_extraction(self):
        """モデル名抽出テスト"""
        # model_name属性がある場合
        mock_model_with_name = Mock()
        mock_model_with_name.model_name = "test_model_name"
        generator = MahjongQuestionGenerator(mock_model_with_name, use_tools=False)
        self.assertEqual(generator.model_name, "test_model_name")
        
        # model属性がある場合
        mock_model_with_model = Mock()
        mock_model_with_model.model = "test_model"
        del mock_model_with_model.model_name
        generator = MahjongQuestionGenerator(mock_model_with_model, use_tools=False)
        self.assertEqual(generator.model_name, "test_model")
        
        # どちらもない場合
        mock_model_unknown = Mock()
        del mock_model_unknown.model_name
        del mock_model_unknown.model
        generator = MahjongQuestionGenerator(mock_model_unknown, use_tools=False)
        self.assertEqual(generator.model_name, "unknown")

    def test_generate_question_simple_mode_with_meld(self):
        """鳴きありの手牌でのシンプルモード問題生成テスト"""
        test_hand_with_meld = {
            "tiles": ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "2p", "2p"],
            "win_tile": "2p",
            "melds": [{"tiles": ["1p", "1p", "1p"], "is_open": True}],
            "dora_indicators": ["1z"],
            "is_riichi": False,
            "is_tsumo": False,
            "player_wind": "east",
            "round_wind": "east"
        }
        
        generator = MahjongQuestionGenerator(self.mock_model, use_tools=False)
        
        with patch('generator.generator.PromptTemplate') as mock_prompt_template:
            mock_prompt = Mock()
            mock_prompt_template.return_value = mock_prompt
            
            mock_chain = Mock()
            mock_chain.invoke.return_value = test_hand_with_meld
            mock_prompt.__or__ = Mock(return_value=mock_chain)
            
            result = generator.generate_question("Generate a test question with meld")
            
            self.assertEqual(result, test_hand_with_meld)
            self.assertIsNotNone(result["melds"])
            self.assertEqual(len(result["melds"]), 1)


if __name__ == '__main__':
    unittest.main()