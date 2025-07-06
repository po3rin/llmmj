import logging
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from entity.entity import Hand
from evaluator.result import EvalResult
from exceptions import HandValidationError, ScoreCalculationError
from llmmj.llmmj import calculate_score, validate_hand

logger = logging.getLogger(__name__)


def hand_2_result(hand: Hand, data: Dict[str, Any], model_name: str) -> EvalResult:
    # 点数計算
    try:
        result = calculate_score(hand)
        if result.fu == data["answer"]["fu"] and result.han == data["answer"]["han"]:
            return EvalResult(
                model=model_name,
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
                model=model_name,
                correct=False,
                is_error=False,
                reason="Incorrect got",
                hand=hand,
                got_answer_han=result.han,
                got_answer_fu=result.fu,
                expected_han=data["answer"]["han"],
                expected_fu=data["answer"]["fu"],
            )
    except ScoreCalculationError as e:
        return EvalResult(
            model=model_name,
            correct=False,
            is_error=True,
            reason=f"Error calculating score: {e!s}",
            error_type=ScoreCalculationError.__name__,
            hand=hand,
            expected_han=data["answer"]["han"],
            expected_fu=data["answer"]["fu"],
        )
    except Exception as e:
        return EvalResult(
            model=model_name,
            correct=False,
            is_error=True,
            error_type="UnknownError",
            reason=f"Error calculating score: {e!s}",
            hand=hand,
            expected_han=data["answer"]["han"],
            expected_fu=data["answer"]["fu"],
        )


def create_error_result(
    model_name: str,
    error: Exception,
    error_type: str,
    data: Optional[Dict[str, Any]] = None,
    hand: Optional[Hand] = None,
) -> EvalResult:
    """Create an error EvalResult based on the exception type."""
    if hand is None:
        hand = Hand(tiles=[], win_tile="")

    result = EvalResult(
        model=model_name,
        correct=False,
        is_error=True,
        error_type=error_type,
        reason=f"{error_type}: {str(error)}",
        hand=hand,
        expected_han=data["answer"].get("han"),
        expected_fu=data["answer"].get("fu"),
    )

    # Add expected values if data is provided
    if data and "answer" in data:
        result.expected_han = data["answer"].get("han")
        result.expected_fu = data["answer"].get("fu")

    return result


def process_hand_generation(
    result: Union[Dict[str, Any], Hand],
    data: Dict[str, Any],
    model_name: str,
) -> Union[Hand, EvalResult]:
    """Process the hand generation result and validate it.

    Returns:
        Hand if successful, EvalResult if there's an error
    """
    # Convert result to Hand object
    try:
        if isinstance(result, dict):
            hand = Hand(**result)
        elif isinstance(result, Hand):
            hand = result
        else:
            return create_error_result(
                model_name=model_name,
                error=ValueError(f"Invalid result type from generator: {type(result)}"),
                error_type="InvalidResultType",
                data=data,
            )
    except Exception as e:
        return create_error_result(
            model_name=model_name,
            error=e,
            error_type="HandCreationError",
            data=data,
        )

    # Validate the hand
    try:
        validate_hand(hand)
        return hand
    except HandValidationError as e:
        logger.error(f"Error validating hand: {e!s}")
        return create_error_result(
            model_name=model_name,
            error=e,
            error_type=HandValidationError.__name__,
            data=data,
            hand=hand,
        )


def result_to_df(eval_results: List[EvalResult]) -> pd.DataFrame:
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
