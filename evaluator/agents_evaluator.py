import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from pydantic import BaseModel, Field

from agents.agents import get_loop_runner, get_sequential_runner, run
from entity.entity import Hand
from llmmj.llmmj import calculate_score, validate_hand

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


class MahjongEvaluatorSequential:
    def __init__(self, runner_type: str = "sequential"):
        self.runner_type = runner_type
        self.app_name = "mahjong_evaluator"
        self.model_name = f"gemini-{runner_type}"

    async def _generate_hand_from_query(
        self,
        query: str,
        app_name: str,
        user_id: str,
        session_id: str,
        data: Dict[str, Any],
    ) -> Hand:
        """Use sequential_run to generate a mahjong hand from a query."""
        try:
            if self.runner_type == "sequential":
                runner = await get_sequential_runner(app_name, user_id, session_id)
            elif self.runner_type == "loop":
                runner = await get_loop_runner(
                    app_name,
                    user_id,
                    session_id,
                    expected_han=data["answer"]["han"],
                    expected_fu=data["answer"]["fu"],
                )
            else:
                raise ValueError(f"Unknown runner_type: {self.runner_type}")

            result = await run(
                runner=runner, user_id=user_id, session_id=session_id, query=query
            )

            # Parse the JSON result
            hand_data = json.loads(result)
            return Hand(**hand_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON result: {e}, raw result: {result}")
            raise
        except Exception as e:
            logger.error(f"Error in _generate_hand_from_query: {e}")
            raise

    def _pipe(self, hand: Hand, data: Dict[str, Any]) -> EvalResult:
        # Handle error cases where hand has empty tiles
        try:
            validate_hand(hand)
        except Exception as e:
            logger.error(f"Error validating hand: {e!s}")
            return EvalResult(
                model=self.model_name,
                correct=False,
                is_error=True,
                reason=f"Error validating hand: {e!s}",
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

    async def evals_async(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        """Asynchronous evaluation of dataset."""
        eval_results: List[EvalResult] = []

        for d in dataset:
            user_id = str(uuid.uuid4())
            session_id = str(uuid.uuid4())
            try:
                hand = await self._generate_hand_from_query(
                    d["query"], self.app_name, user_id, session_id, d
                )
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

    def evals(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        """Synchronous wrapper for evals_async."""
        try:
            # Check if we're in an async context (like Jupyter)
            loop = asyncio.get_running_loop()
            # If we're already in an event loop, we need to handle it differently
            import concurrent.futures
            import threading

            # Create a new thread to run the async function
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.evals_async(dataset))
                return future.result()
        except RuntimeError:
            # No event loop running, use asyncio.run normally
            return asyncio.run(self.evals_async(dataset))

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
