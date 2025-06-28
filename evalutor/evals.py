import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field

from entity.entity import Hand
from generator.generator import (
    MahjongQuestionGenerator,
    generate_question_prompt_template,
)
from llmmj.llmmj import calculate_score, validate_meld, validate_tiles

logger = logging.getLogger(__name__)


class EvalResult(BaseModel):
    model: str = Field("unknown", description="モデル名")
    correct: bool = Field(..., description="正解かどうか")
    is_error: bool = Field(..., description="エラーで処理が停止したかどうか")
    reason: str = Field(..., description="理由")
    hand: Hand = Field(..., description="手牌")
    got_answer_han: Optional[int] = Field(None, description="得られた答えの翻数")
    got_answer_fu: Optional[int] = Field(None, description="得られた答えの符数")
    expected_han: int = Field(..., description="期待する答えの翻数")
    expected_fu: int = Field(..., description="期待する答えの符数")


class MahjongEvaluator:
    def __init__(self, generator: MahjongQuestionGenerator):
        self.generator = generator
        self.model_name = generator.model_name

    def _pipe(self, hand: Hand, data: Dict[str, Any]) -> EvalResult:
        # Handle error cases where hand has empty tiles
        if not hand.tiles:
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=True,
                reason="Empty hand tiles (error case)",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )

        # 手牌の形式チェック
        if not validate_tiles(hand.tiles):
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=False,
                reason="Invalid tile format in hand",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )
        # ドラ表示牌の形式チェック
        if hand.dora_indicators and not validate_tiles(hand.dora_indicators):
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=False,
                reason="Invalid tile format in dora indicators",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )
        # 鳴きの形式チェック
        if hand.melds and not validate_meld(hand.tiles, hand.melds):
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=False,
                reason="Invalid meld in hand",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )
        # # 手牌の枚数チェック
        # if hand.tiles and len(hand.tiles) != 14:
        #     return EvalResult(
        #         model=self.model_name,
        #         correct=False,
        #         is_error=False,
        #         reason="Invalid tile count in hand",
        #         hand=hand,
        #         expected_han=data["answer"]["han"],
        #         expected_fu=data["answer"]["fu"],
        #     )
        # 和了牌の形式チェック
        if hand.win_tile and hand.win_tile not in hand.tiles:
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=False,
                reason="Invalid win tile in hand",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )

        # 点数計算
        try:
            result = calculate_score(hand)
            if (
                result.fu == data["answer"]["fu"]
                and result.han == data["answer"]["han"]
            ):
                return EvalResult(
                    model=self.model_name,
                    correct=True,
                    is_error=False,
                    reason="Correct",
                    hand=hand,
                    got_answer_han=result.han,
                    got_answer_fu=result.fu,
                    expected_han=data["answer"]["han"],
                    expected_fu=data["answer"]["fu"],
                )
            else:
                return EvalResult(
                    model=self.model_name,
                    correct=False,
                    is_error=False,
                    reason="Incorrect got",
                    hand=hand,
                    got_answer_han=result.han,
                    got_answer_fu=result.fu,
                    expected_han=data["answer"]["han"],
                    expected_fu=data["answer"]["fu"],
                )
        except Exception as e:
            logger.error(f"Error calculating score: {e}")
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=True,
                reason="Error calculating score",
                hand=hand,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )

    def evals(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        eval_results: List[EvalResult] = []
        for d in dataset:
            try:
                result = self.generator.generate_question(d["query"])
                # Check if result is a valid dictionary/object that can be used to create Hand
                if isinstance(result, dict):
                    hand = Hand(**result)
                elif isinstance(result, Hand):
                    hand = result
                else:
                    # If result is not a dict or Hand object, create an error result
                    logger.error(
                        f"Invalid result type from generator: {type(result)}, value: {result}"
                    )
                    eval_result = EvalResult(
                        model=self.model_name,
                        correct=False,
                        is_error=True,
                        reason=f"Invalid result type from generator: {type(result)}",
                        hand=Hand(tiles=[], win_tile=""),
                        expected_han=d["answer"]["han"],
                        expected_fu=d["answer"]["fu"],
                    )
                    eval_results.append(eval_result)
                    continue
            except Exception as e:
                logger.error(f"Error generating question: {e}")
                # Create an error result instead of raising the exception
                eval_result = EvalResult(
                    model=self.model_name,
                    correct=False,
                    is_error=True,
                    reason=f"Error generating question: {str(e)}",
                    hand=Hand(tiles=[], win_tile=""),
                    expected_han=d["answer"]["han"],
                    expected_fu=d["answer"]["fu"],
                )
                eval_results.append(eval_result)
                continue

            eval_result = self._pipe(hand, d)
            eval_results.append(eval_result)

        return self.result_to_df(eval_results)

    def result_to_df(self, eval_results: List[EvalResult]) -> pd.DataFrame:
        records = []
        for result in eval_results:
            record = result.model_dump(exclude={"hand"})
            hand_dict = result.hand.model_dump()
            for key, value in hand_dict.items():
                record[f"hand_{key}"] = value

            # Convert boolean values to integers
            for key, value in record.items():
                if isinstance(value, bool):
                    record[key] = int(value)

            records.append(record)

        return pd.DataFrame(records)


class MultiModelEvaluator:
    def __init__(
        self,
        models: List[BaseChatModel],
        query_template: str = generate_question_prompt_template,
        use_tools: bool = False,
    ):
        self.models = models
        self.query_template = query_template
        self.use_tools = use_tools

    def evals(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        eval_results: List[pd.DataFrame] = []
        for model in self.models:
            generator = MahjongQuestionGenerator(
                model, query_template=self.query_template, use_tools=self.use_tools
            )
            evaluator = MahjongEvaluator(generator)
            eval_results.append(evaluator.evals(dataset))
        return pd.concat(eval_results).reset_index(drop=True)
