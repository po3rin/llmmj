import asyncio
import json
import unittest
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd

from entity.entity import Hand
from evaluator.agents_evaluator import MahjongMultiAgentsEvaluator
from evaluator.result import EvalResult
from exceptions import AgentSetupError, JSONParseError


class TestMahjongMultiAgentsEvaluator(unittest.TestCase):
    def setUp(self):
        """テストの準備"""
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

    def test_init_sequential(self):
        """シーケンシャルモードでの初期化テスト"""
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        self.assertEqual(evaluator.runner_type, "sequential")
        self.assertEqual(evaluator.app_name, "mahjong_evaluator")
        self.assertEqual(evaluator.model_name, "gemini-sequential")

    def test_init_loop(self):
        """ループモードでの初期化テスト"""
        evaluator = MahjongMultiAgentsEvaluator(runner_type="loop")
        
        self.assertEqual(evaluator.runner_type, "loop")
        self.assertEqual(evaluator.app_name, "mahjong_evaluator")
        self.assertEqual(evaluator.model_name, "gemini-loop")

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.process_hand_generation')
    @patch('evaluator.agents_evaluator.hand_2_result')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_generate_hand_from_query_sequential_success(
        self, mock_result_to_df, mock_hand_2_result, mock_process_hand, mock_run, mock_get_runner
    ):
        """シーケンシャルモードでの手牌生成成功テスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return JSON
        mock_run.return_value = json.dumps(self.test_hand_data)
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        result = await evaluator._generate_hand_from_query(
            "test query",
            "test_app",
            "test_user",
            "test_session",
            self.test_dataset[0]
        )
        
        # Verify result
        self.assertIsInstance(result, Hand)
        self.assertEqual(result.tiles, self.test_hand_data["tiles"])
        self.assertEqual(result.win_tile, self.test_hand_data["win_tile"])
        
        # Verify calls
        mock_get_runner.assert_called_once_with("test_app", "test_user", "test_session")
        mock_run.assert_called_once_with(
            runner=mock_runner,
            user_id="test_user",
            session_id="test_session",
            query="test query"
        )

    @patch('evaluator.agents_evaluator.get_loop_runner')
    @patch('evaluator.agents_evaluator.run')
    async def test_generate_hand_from_query_loop_success(self, mock_run, mock_get_runner):
        """ループモードでの手牌生成成功テスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return JSON
        mock_run.return_value = json.dumps(self.test_hand_data)
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="loop")
        
        result = await evaluator._generate_hand_from_query(
            "test query",
            "test_app",
            "test_user",
            "test_session",
            self.test_dataset[0]
        )
        
        # Verify result
        self.assertIsInstance(result, Hand)
        self.assertEqual(result.tiles, self.test_hand_data["tiles"])
        self.assertEqual(result.win_tile, self.test_hand_data["win_tile"])
        
        # Verify calls
        mock_get_runner.assert_called_once_with("test_app", "test_user", "test_session")
        mock_run.assert_called_once_with(
            runner=mock_runner,
            user_id="test_user",
            session_id="test_session",
            query="test query"
        )

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    async def test_generate_hand_from_query_json_parse_error(self, mock_run, mock_get_runner):
        """JSON解析エラーテスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return invalid JSON
        mock_run.return_value = "invalid json"
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        with self.assertRaises(JSONParseError):
            await evaluator._generate_hand_from_query(
                "test query",
                "test_app",
                "test_user",
                "test_session",
                self.test_dataset[0]
            )

    async def test_generate_hand_from_query_unknown_runner_type(self):
        """未知のランナータイプエラーテスト"""
        evaluator = MahjongMultiAgentsEvaluator(runner_type="unknown")
        
        with self.assertRaises(AgentSetupError):
            await evaluator._generate_hand_from_query(
                "test query",
                "test_app",
                "test_user",
                "test_session",
                self.test_dataset[0]
            )

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.process_hand_generation')
    @patch('evaluator.agents_evaluator.hand_2_result')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_evals_async_success(
        self, mock_result_to_df, mock_hand_2_result, mock_process_hand, mock_run, mock_get_runner
    ):
        """非同期評価成功テスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return JSON
        mock_run.return_value = json.dumps(self.test_hand_data)
        
        # Mock processing functions
        mock_process_hand.return_value = self.test_hand
        
        test_eval_result = EvalResult(
            model="gemini-sequential",
            correct=True,
            is_error=False,
            reason="Correct",
            hand=self.test_hand,
            got_answer_han=1,
            got_answer_fu=30,
            expected_han=1,
            expected_fu=30
        )
        mock_hand_2_result.return_value = test_eval_result
        
        # Mock result_to_df
        mock_df = pd.DataFrame([{"test": "data"}])
        mock_result_to_df.return_value = mock_df
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        result = await evaluator.evals_async(self.test_dataset)
        
        # Verify calls
        self.assertEqual(mock_get_runner.call_count, 2)
        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(mock_process_hand.call_count, 2)
        self.assertEqual(mock_hand_2_result.call_count, 2)
        mock_result_to_df.assert_called_once()
        
        # Verify result
        self.assertEqual(result.iloc[0]["test"], "data")

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.create_error_result')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_evals_async_agent_setup_error(
        self, mock_result_to_df, mock_create_error, mock_run, mock_get_runner
    ):
        """エージェントセットアップエラーテスト"""
        # Mock runner to raise AgentSetupError
        mock_get_runner.side_effect = AgentSetupError("Setup failed")
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        with self.assertRaises(AgentSetupError):
            await evaluator.evals_async(self.test_dataset)

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.create_error_result')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_evals_async_json_parse_error(
        self, mock_result_to_df, mock_create_error, mock_run, mock_get_runner
    ):
        """JSON解析エラーテスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return invalid JSON
        mock_run.return_value = "invalid json"
        
        # Mock create_error_result
        error_result = EvalResult(
            model="gemini-sequential",
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
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        result = await evaluator.evals_async(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_create_error.call_count, 2)
        mock_result_to_df.assert_called_once()

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.create_error_result')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_evals_async_unknown_error(
        self, mock_result_to_df, mock_create_error, mock_run, mock_get_runner
    ):
        """未知のエラーテスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to raise unknown error
        mock_run.side_effect = Exception("Unknown error")
        
        # Mock create_error_result
        error_result = EvalResult(
            model="gemini-sequential",
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
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        result = await evaluator.evals_async(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_create_error.call_count, 2)
        mock_result_to_df.assert_called_once()

    @patch('evaluator.agents_evaluator.get_sequential_runner')
    @patch('evaluator.agents_evaluator.run')
    @patch('evaluator.agents_evaluator.process_hand_generation')
    @patch('evaluator.agents_evaluator.result_to_df')
    async def test_evals_async_process_hand_error(
        self, mock_result_to_df, mock_process_hand, mock_run, mock_get_runner
    ):
        """手牌処理エラーテスト"""
        # Mock runner
        mock_runner = Mock()
        mock_get_runner.return_value = mock_runner
        
        # Mock run to return JSON
        mock_run.return_value = json.dumps(self.test_hand_data)
        
        # Mock process_hand_generation to return error result
        error_result = EvalResult(
            model="gemini-sequential",
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
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        result = await evaluator.evals_async(self.test_dataset)
        
        # Verify error handling
        self.assertEqual(mock_process_hand.call_count, 2)
        mock_result_to_df.assert_called_once()

    @patch('evaluator.agents_evaluator.asyncio.run')
    @patch('evaluator.agents_evaluator.concurrent.futures.ThreadPoolExecutor')
    def test_evals_sync_wrapper_with_executor(self, mock_executor, mock_asyncio_run):
        """同期ラッパーのテスト（ThreadPoolExecutor使用）"""
        # Mock ThreadPoolExecutor
        mock_future = Mock()
        mock_future.result.return_value = pd.DataFrame([{"test": "data"}])
        mock_executor_instance = Mock()
        mock_executor_instance.__enter__.return_value = mock_executor_instance
        mock_executor_instance.__exit__.return_value = None
        mock_executor_instance.submit.return_value = mock_future
        mock_executor.return_value = mock_executor_instance
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        # Mock get_running_loop to raise RuntimeError initially, then succeed
        with patch('evaluator.agents_evaluator.asyncio.get_running_loop', side_effect=RuntimeError()):
            result = evaluator.evals(self.test_dataset)
        
        # Verify executor was used
        mock_executor.assert_called_once()
        mock_executor_instance.submit.assert_called_once()
        self.assertEqual(result.iloc[0]["test"], "data")

    @patch('evaluator.agents_evaluator.asyncio.run')
    def test_evals_sync_wrapper_with_asyncio_run(self, mock_asyncio_run):
        """同期ラッパーのテスト（asyncio.run使用）"""
        # Mock asyncio.run
        mock_asyncio_run.return_value = pd.DataFrame([{"test": "data"}])
        
        evaluator = MahjongMultiAgentsEvaluator(runner_type="sequential")
        
        # Mock get_running_loop to raise RuntimeError (no event loop)
        with patch('evaluator.agents_evaluator.asyncio.get_running_loop', side_effect=RuntimeError()):
            result = evaluator.evals(self.test_dataset)
        
        # Verify asyncio.run was used
        mock_asyncio_run.assert_called_once()
        self.assertEqual(result.iloc[0]["test"], "data")


if __name__ == '__main__':
    unittest.main()