import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from entity.entity import Hand
from evaluator.libs import (
    create_error_result,
    hand_2_result,
    process_hand_generation,
    result_to_df,
)
from evaluator.result import EvalResult
from exceptions import AgentSetupError, JSONParseError
from runner.runner import get_loop_runner, get_sequential_runner, run

logger = logging.getLogger(__name__)


class MahjongMultiAgentsEvaluator:
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

        if self.runner_type == "sequential":
            runner = await get_sequential_runner(app_name, user_id, session_id)
        elif self.runner_type == "loop":
            runner = await get_loop_runner(
                app_name,
                user_id,
                session_id,
                # expected_han=data["answer"]["han"],
                # expected_fu=data["answer"]["fu"],
            )
        else:
            raise AgentSetupError(f"Unknown runner_type: {self.runner_type}")

        result = await run(
            runner=runner, user_id=user_id, session_id=session_id, query=query
        )

        # Parse the JSON result
        try:
            hand_data = json.loads(result)
        except Exception as e:
            raise JSONParseError(f"Error parsing JSON: {e!s}, result: {result}") from e

        return Hand(**hand_data)

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
            except AgentSetupError as e:
                logger.error(f"Error setting up agent: {e!s}")
                raise
            except JSONParseError as e:
                eval_result = create_error_result(
                    model_name=self.model_name,
                    error=e,
                    error_type=JSONParseError.__name__,
                    data=d,
                )
                eval_results.append(eval_result)
                continue
            except Exception as e:
                eval_result = create_error_result(
                    model_name=self.model_name,
                    error=e,
                    error_type="UnknownError",
                    data=d,
                )
                eval_results.append(eval_result)
                continue

            # Process and validate the hand
            hand_or_error = process_hand_generation(hand, d, self.model_name)
            if isinstance(hand_or_error, EvalResult):
                eval_results.append(hand_or_error)
                continue

            # Calculate score and create result
            eval_result = hand_2_result(hand_or_error, d, self.model_name)
            eval_results.append(eval_result)

        return result_to_df(eval_results)

    def evals(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        """Synchronous wrapper for evals_async."""
        try:
            # # Check if we're in an async context (like Jupyter)
            # loop = asyncio.get_running_loop()
            # If we're already in an event loop, we need to handle it differently
            import concurrent.futures

            # Create a new thread to run the async function
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.evals_async(dataset))
                return future.result()
        except RuntimeError:
            # No event loop running, use asyncio.run normally
            return asyncio.run(self.evals_async(dataset))
