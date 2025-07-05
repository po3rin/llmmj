import logging
from typing import Any, Dict, List

import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel

from entity.entity import Hand
from evaluator.result import EvalResult
from generator.generator import (
    MahjongQuestionGenerator,
    generate_question_prompt_template,
)
from llmmj.llmmj import calculate_score, validate_hand

logger = logging.getLogger(__name__)


class MahjongEvaluator:
    def __init__(self, generator: MahjongQuestionGenerator):
        self.generator = generator
        self.model_name = generator.model_name

    def _hand_2_result(self, hand: Hand, data: Dict[str, Any]) -> EvalResult:
        # Use centralized validate_hand function
        try:
            validate_hand(hand)
        except ValueError as e:
            # Map the error messages to appropriate reasons
            error_msg = str(e)
            is_error = False

            if "tiles is required" in error_msg:
                is_error = True
                reason = "Empty hand tiles (error case)"
            elif "Invalid tile format in tiles" in error_msg:
                reason = "Invalid tile format in hand"
            elif "Invalid tile format in dora indicators" in error_msg:
                reason = "Invalid tile format in dora indicators"
            elif "Invalid meld in hand" in error_msg:
                reason = "Invalid meld in hand"
            elif "Invalid tile count in hand" in error_msg:
                reason = "Invalid tile count in hand"
            elif "Invalid win tile in hand" in error_msg:
                reason = "Invalid win tile in hand"
            else:
                reason = error_msg

            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=is_error,
                reason=reason,
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

            eval_result = self._hand_2_result(hand, d)
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
