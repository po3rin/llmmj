import unittest
from unittest.mock import Mock, patch
import pandas as pd

from entity.entity import Hand, MeldInfo
from evaluator.libs import (
    hand_2_result, 
    create_error_result, 
    process_hand_generation,
    result_to_df
)
from evaluator.result import EvalResult
from exceptions import HandValidationError, ScoreCalculationError
from llmmj.llmmj import ScoreResponse


class TestEvaluatorLibs(unittest.TestCase):
    def setUp(self):
        """テストの準備"""
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
        
        # テスト用のデータセット項目
        self.test_data = {
            "query": "Generate a test question",
            "answer": {"han": 1, "fu": 30}
        }
        
        # テスト用のスコア応答
        self.test_score_response = ScoreResponse(
            han=1,
            fu=30,
            score=1000,
            yaku=["リーチ"],
            fu_details=[{"name": "基本符", "fu": 20}],
            error=None
        )

    @patch('evaluator.libs.calculate_score')
    def test_hand_2_result_correct(self, mock_calculate_score):
        """正答の場合のテスト"""
        # Mock calculate_score to return correct answer
        mock_calculate_score.return_value = self.test_score_response
        
        result = hand_2_result(self.test_hand, self.test_data, "test_model")
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.model, "test_model")
        self.assertTrue(result.correct)
        self.assertFalse(result.is_error)
        self.assertEqual(result.reason, "Correct")
        self.assertEqual(result.got_answer_han, 1)
        self.assertEqual(result.got_answer_fu, 30)
        self.assertEqual(result.expected_han, 1)
        self.assertEqual(result.expected_fu, 30)

    @patch('evaluator.libs.calculate_score')
    def test_hand_2_result_incorrect(self, mock_calculate_score):
        """誤答の場合のテスト"""
        # Mock calculate_score to return incorrect answer
        incorrect_response = ScoreResponse(
            han=2,
            fu=40,
            score=2000,
            yaku=["リーチ", "タンヤオ"],
            fu_details=[{"name": "基本符", "fu": 20}],
            error=None
        )
        mock_calculate_score.return_value = incorrect_response
        
        result = hand_2_result(self.test_hand, self.test_data, "test_model")
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.model, "test_model")
        self.assertFalse(result.correct)
        self.assertFalse(result.is_error)
        self.assertEqual(result.reason, "Incorrect got")
        self.assertEqual(result.got_answer_han, 2)
        self.assertEqual(result.got_answer_fu, 40)
        self.assertEqual(result.expected_han, 1)
        self.assertEqual(result.expected_fu, 30)

    @patch('evaluator.libs.calculate_score')
    def test_hand_2_result_score_calculation_error(self, mock_calculate_score):
        """スコア計算エラーの場合のテスト"""
        # Mock calculate_score to raise ScoreCalculationError
        mock_calculate_score.side_effect = ScoreCalculationError("Invalid hand")
        
        result = hand_2_result(self.test_hand, self.test_data, "test_model")
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.model, "test_model")
        self.assertFalse(result.correct)
        self.assertTrue(result.is_error)
        self.assertEqual(result.error_type, "ScoreCalculationError")
        self.assertEqual(result.reason, "Error calculating score: Invalid hand")
        self.assertEqual(result.expected_han, 1)
        self.assertEqual(result.expected_fu, 30)

    @patch('evaluator.libs.calculate_score')
    def test_hand_2_result_unknown_error(self, mock_calculate_score):
        """未知のエラーの場合のテスト"""
        # Mock calculate_score to raise unknown error
        mock_calculate_score.side_effect = Exception("Unknown error")
        
        result = hand_2_result(self.test_hand, self.test_data, "test_model")
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.model, "test_model")
        self.assertFalse(result.correct)
        self.assertTrue(result.is_error)
        self.assertEqual(result.error_type, "UnknownError")
        self.assertEqual(result.reason, "Error calculating score: Unknown error")

    def test_create_error_result_basic(self):
        """基本的なエラー結果作成テスト"""
        error = ValueError("Test error")
        result = create_error_result(
            model_name="test_model",
            error=error,
            error_type="ValueError",
            data=self.test_data
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.model, "test_model")
        self.assertFalse(result.correct)
        self.assertTrue(result.is_error)
        self.assertEqual(result.error_type, "ValueError")
        self.assertEqual(result.reason, "ValueError: Test error")
        self.assertEqual(result.expected_han, 1)
        self.assertEqual(result.expected_fu, 30)

    def test_create_error_result_with_hand(self):
        """手牌付きエラー結果作成テスト"""
        error = HandValidationError("Invalid tiles")
        result = create_error_result(
            model_name="test_model",
            error=error,
            error_type="HandValidationError",
            data=self.test_data,
            hand=self.test_hand
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.hand, self.test_hand)
        self.assertEqual(result.error_type, "HandValidationError")

    def test_create_error_result_no_data(self):
        """データなしエラー結果作成テスト"""
        error = Exception("Test error")
        result = create_error_result(
            model_name="test_model",
            error=error,
            error_type="Exception"
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertIsNone(result.expected_han)
        self.assertIsNone(result.expected_fu)

    @patch('evaluator.libs.validate_hand')
    def test_process_hand_generation_dict_success(self, mock_validate_hand):
        """辞書形式の手牌処理成功テスト"""
        # Mock validate_hand to pass
        mock_validate_hand.return_value = None
        
        result = process_hand_generation(
            self.test_hand_data,
            self.test_data,
            "test_model"
        )
        
        self.assertIsInstance(result, Hand)
        self.assertEqual(result.tiles, self.test_hand_data["tiles"])
        self.assertEqual(result.win_tile, self.test_hand_data["win_tile"])
        mock_validate_hand.assert_called_once()

    @patch('evaluator.libs.validate_hand')
    def test_process_hand_generation_hand_success(self, mock_validate_hand):
        """Hand形式の手牌処理成功テスト"""
        # Mock validate_hand to pass
        mock_validate_hand.return_value = None
        
        result = process_hand_generation(
            self.test_hand,
            self.test_data,
            "test_model"
        )
        
        self.assertIsInstance(result, Hand)
        self.assertEqual(result, self.test_hand)
        mock_validate_hand.assert_called_once()

    def test_process_hand_generation_invalid_type(self):
        """不正な型の手牌処理テスト"""
        # Use a type that's not Dict or Hand to test invalid type handling
        invalid_input = 123  # int type, not Dict or Hand
        result = process_hand_generation(
            invalid_input,  # type: ignore
            self.test_data,
            "test_model"
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.error_type, "InvalidResultType")
        self.assertTrue(result.is_error)

    def test_process_hand_generation_hand_creation_error(self):
        """Hand作成エラーテスト"""
        invalid_hand_data = {
            "tiles": [],  # Invalid: no tiles
            "win_tile": "invalid_tile"  # Invalid tile format
        }
        
        result = process_hand_generation(
            invalid_hand_data,
            self.test_data,
            "test_model"
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.error_type, "HandCreationError")
        self.assertTrue(result.is_error)

    @patch('evaluator.libs.validate_hand')
    def test_process_hand_generation_validation_error(self, mock_validate_hand):
        """手牌検証エラーテスト"""
        # Mock validate_hand to raise HandValidationError
        mock_validate_hand.side_effect = HandValidationError("Invalid hand")
        
        result = process_hand_generation(
            self.test_hand_data,
            self.test_data,
            "test_model"
        )
        
        self.assertIsInstance(result, EvalResult)
        self.assertEqual(result.error_type, "HandValidationError")
        self.assertTrue(result.is_error)

    def test_result_to_df(self):
        """結果のDataFrame変換テスト"""
        # テスト用の結果リスト
        results = [
            EvalResult(
                model="model1",
                correct=True,
                is_error=False,
                reason="Correct",
                hand=self.test_hand,
                got_answer_han=1,
                got_answer_fu=30,
                expected_han=1,
                expected_fu=30
            ),
            EvalResult(
                model="model2",
                correct=False,
                is_error=True,
                error_type="JSONParseError",
                reason="Invalid JSON",
                hand=Hand(tiles=[], win_tile=""),
                expected_han=2,
                expected_fu=40
            )
        ]
        
        df = result_to_df(results)
        
        # DataFrame の基本的な検証
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        
        # 最初の行の検証
        self.assertEqual(df.iloc[0]["model"], "model1")
        self.assertEqual(df.iloc[0]["correct"], 1)  # boolean -> int
        self.assertEqual(df.iloc[0]["is_error"], 0)  # boolean -> int
        self.assertEqual(df.iloc[0]["reason"], "Correct")
        
        # 2番目の行の検証
        self.assertEqual(df.iloc[1]["model"], "model2")
        self.assertEqual(df.iloc[1]["correct"], 0)  # boolean -> int
        self.assertEqual(df.iloc[1]["is_error"], 1)  # boolean -> int
        self.assertEqual(df.iloc[1]["error_type"], "JSONParseError")
        
        # 手牌データが展開されていることを確認
        self.assertIn("hand_tiles", df.columns)
        self.assertIn("hand_win_tile", df.columns)
        self.assertIn("hand_is_riichi", df.columns)

    def test_result_to_df_with_melds(self):
        """鳴きありの結果のDataFrame変換テスト"""
        # 鳴きありの手牌
        hand_with_meld = Hand(
            tiles=["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "1p", "1p", "2p", "2p"],
            win_tile="2p",
            melds=[MeldInfo(tiles=["1p", "1p", "1p"], is_open=True)],
            dora_indicators=["1z"],
            is_riichi=False,
            is_tsumo=False,
            player_wind="east",
            round_wind="east"
        )
        
        results = [
            EvalResult(
                model="test_model",
                correct=True,
                is_error=False,
                reason="Correct with meld",
                hand=hand_with_meld,
                got_answer_han=1,
                got_answer_fu=30,
                expected_han=1,
                expected_fu=30
            )
        ]
        
        df = result_to_df(results)
        
        # DataFrame の基本的な検証
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        
        # 鳴きデータが含まれていることを確認
        self.assertIn("hand_melds", df.columns)
        self.assertIsNotNone(df.iloc[0]["hand_melds"])


if __name__ == '__main__':
    unittest.main()