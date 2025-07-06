import unittest
from unittest.mock import Mock, patch
import pandas as pd

from entity.entity import Hand
from evaluator.evaluator import MahjongEvaluator, MultiModelEvaluator
from evaluator.result import EvalResult
from exceptions import AgentSetupError, JSONParseError
from generator.generator import MahjongQuestionGenerator


class TestMahjongEvaluator(unittest.TestCase):
    def setUp(self):
        """テストの準備"""
        self.mock_model = Mock()
        self.mock_model.model_name = "test_model"
        
        # Mock generator
        self.mock_generator = Mock(spec=MahjongQuestionGenerator)
        self.mock_generator.model_name = "test_model"
        
        # テスト用データセット
        self.test_dataset = [
            {
                "query": "Generate a test question",
                "answer": {"han": 1, "fu": 30}
            },
            {
                "query": "Generate another test question",
                "answer": {"han": 2, "fu": 40}
            }
        ]
        
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
        
        # テスト用のEvalResult
        self.test_eval_result = EvalResult(
            model="test_model",
            correct=True,
            is_error=False,
            reason="Test reason",
            hand=self.test_hand,
            got_answer_han=1,
            got_answer_fu=30,
            expected_han=1,
            expected_fu=30
        )

    def test_init(self):
        """初期化テスト"""
        evaluator = MahjongEvaluator(self.mock_generator)
        
        self.assertEqual(evaluator.generator, self.mock_generator)
        self.assertEqual(evaluator.model_name, "test_model")

    @patch('evaluator.evaluator.process_hand_generation')
    @patch('evaluator.evaluator.hand_2_result')
    @patch('evaluator.evaluator.result_to_df')
    def test_evals_success(self, mock_result_to_df, mock_hand_2_result, mock_process_hand):
        """評価成功テスト"""
        # Mock the generator to return test hand data
        self.mock_generator.generate_question.return_value = self.test_hand_data
        
        # Mock the processing functions
        mock_process_hand.return_value = self.test_hand
        mock_hand_2_result.return_value = self.test_eval_result
        
        # Mock result_to_df
        mock_df = pd.DataFrame([{"test": "data"}])
        mock_result_to_df.return_value = mock_df
        
        evaluator = MahjongEvaluator(self.mock_generator)
        result = evaluator.evals(self.test_dataset)
        
        # Verify calls
        self.assertEqual(self.mock_generator.generate_question.call_count, 2)
        self.assertEqual(mock_process_hand.call_count, 2)
        self.assertEqual(mock_hand_2_result.call_count, 2)
        mock_result_to_df.assert_called_once()
        
        # Verify result
        self.assertEqual(result.iloc[0]["test"], "data")

    @patch('evaluator.evaluator.create_error_result')
    @patch('evaluator.evaluator.result_to_df')
    def test_evals_json_parse_error(self, mock_result_to_df, mock_create_error):
        """JSON解析エラーテスト"""
        # Mock the generator to raise JSONParseError
        self.mock_generator.generate_question.side_effect = JSONParseError("Invalid JSON")
        
        # Mock create_error_result
        error_result = EvalResult(
            model="test_model",
            correct=False,
            is_error=True,
            error_type="JSONParseError",
            reason="JSONParseError: Invalid JSON",
            hand=Hand(tiles=[], win_tile=""),
            expected_han=1,
            expected_fu=30
        )
        mock_create_error.return_value = error_result
        
        # Mock result_to_df
        mock_df = pd.DataFrame([{"error": "data"}])
        mock_result_to_df.return_value = mock_df
        
        evaluator = MahjongEvaluator(self.mock_generator)
        result = evaluator.evals(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_create_error.call_count, 2)
        mock_result_to_df.assert_called_once()

    def test_evals_agent_setup_error(self):
        """エージェントセットアップエラーテスト"""
        # Mock the generator to raise AgentSetupError
        self.mock_generator.generate_question.side_effect = AgentSetupError("Setup failed")
        
        evaluator = MahjongEvaluator(self.mock_generator)
        
        with self.assertRaises(AgentSetupError):
            evaluator.evals(self.test_dataset)

    @patch('evaluator.evaluator.create_error_result')
    @patch('evaluator.evaluator.result_to_df')
    def test_evals_unknown_error(self, mock_result_to_df, mock_create_error):
        """未知のエラーテスト"""
        # Mock the generator to raise unknown error
        self.mock_generator.generate_question.side_effect = Exception("Unknown error")
        
        # Mock create_error_result
        error_result = EvalResult(
            model="test_model",
            correct=False,
            is_error=True,
            error_type="UnknownError",
            reason="UnknownError: Unknown error",
            hand=Hand(tiles=[], win_tile=""),
            expected_han=1,
            expected_fu=30
        )
        mock_create_error.return_value = error_result
        
        # Mock result_to_df
        mock_df = pd.DataFrame([{"error": "data"}])
        mock_result_to_df.return_value = mock_df
        
        evaluator = MahjongEvaluator(self.mock_generator)
        result = evaluator.evals(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_create_error.call_count, 2)
        mock_result_to_df.assert_called_once()

    @patch('evaluator.evaluator.process_hand_generation')
    @patch('evaluator.evaluator.result_to_df')
    def test_evals_process_hand_error(self, mock_result_to_df, mock_process_hand):
        """手牌処理エラーテスト"""
        # Mock the generator to return test hand data
        self.mock_generator.generate_question.return_value = self.test_hand_data
        
        # Mock process_hand_generation to return error result
        error_result = EvalResult(
            model="test_model",
            correct=False,
            is_error=True,
            error_type="HandValidationError",
            reason="Invalid hand",
            hand=self.test_hand,
            expected_han=1,
            expected_fu=30
        )
        mock_process_hand.return_value = error_result
        
        # Mock result_to_df
        mock_df = pd.DataFrame([{"error": "data"}])
        mock_result_to_df.return_value = mock_df
        
        evaluator = MahjongEvaluator(self.mock_generator)
        result = evaluator.evals(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_process_hand.call_count, 2)
        mock_result_to_df.assert_called_once()


class TestMultiModelEvaluator(unittest.TestCase):
    def setUp(self):
        """テストの準備"""
        self.mock_model1 = Mock()
        self.mock_model1.model_name = "model1"
        
        self.mock_model2 = Mock()
        self.mock_model2.model_name = "model2"
        
        self.models = [self.mock_model1, self.mock_model2]
        
        # テスト用データセット
        self.test_dataset = [
            {
                "query": "Generate a test question",
                "answer": {"han": 1, "fu": 30}
            }
        ]

    def test_init(self):
        """初期化テスト"""
        evaluator = MultiModelEvaluator(self.models)
        
        self.assertEqual(evaluator.models, self.models)
        self.assertFalse(evaluator.use_tools)

    def test_init_with_custom_template(self):
        """カスタムテンプレートでの初期化テスト"""
        custom_template = "Custom template: {query}"
        evaluator = MultiModelEvaluator(
            self.models, 
            query_template=custom_template,
            use_tools=True
        )
        
        self.assertEqual(evaluator.query_template, custom_template)
        self.assertTrue(evaluator.use_tools)

    @patch('evaluator.evaluator.MahjongQuestionGenerator')
    @patch('evaluator.evaluator.MahjongEvaluator')
    def test_evals(self, mock_evaluator_class, mock_generator_class):
        """評価テスト"""
        # Mock generator instances
        mock_generator1 = Mock()
        mock_generator2 = Mock()
        mock_generator_class.side_effect = [mock_generator1, mock_generator2]
        
        # Mock evaluator instances
        mock_evaluator1 = Mock()
        mock_evaluator2 = Mock()
        mock_evaluator_class.side_effect = [mock_evaluator1, mock_evaluator2]
        
        # Mock evaluation results
        df1 = pd.DataFrame([{"model": "model1", "correct": True}])
        df2 = pd.DataFrame([{"model": "model2", "correct": False}])
        mock_evaluator1.evals.return_value = df1
        mock_evaluator2.evals.return_value = df2
        
        evaluator = MultiModelEvaluator(self.models)
        result = evaluator.evals(self.test_dataset)
        
        # Verify generator creation
        self.assertEqual(mock_generator_class.call_count, 2)
        mock_generator_class.assert_any_call(
            self.mock_model1, 
            query_template=evaluator.query_template,
            use_tools=False
        )
        mock_generator_class.assert_any_call(
            self.mock_model2, 
            query_template=evaluator.query_template,
            use_tools=False
        )
        
        # Verify evaluator creation
        self.assertEqual(mock_evaluator_class.call_count, 2)
        mock_evaluator_class.assert_any_call(mock_generator1)
        mock_evaluator_class.assert_any_call(mock_generator2)
        
        # Verify evaluation calls
        mock_evaluator1.evals.assert_called_once_with(self.test_dataset)
        mock_evaluator2.evals.assert_called_once_with(self.test_dataset)
        
        # Verify result concatenation
        self.assertEqual(len(result), 2)
        self.assertEqual(result.iloc[0]["model"], "model1")
        self.assertEqual(result.iloc[1]["model"], "model2")


if __name__ == '__main__':
    unittest.main()