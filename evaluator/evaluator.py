import logging
from typing import Any, Dict, List

import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel

from evaluator.libs import (
    create_error_result,
    hand_2_result,
    process_hand_generation,
    result_to_df,
)
from evaluator.result import EvalResult
from exceptions import AgentSetupError, JSONParseError
from generator.generator import (
    MahjongQuestionGenerator,
    generate_question_prompt_template,
)

logger = logging.getLogger(__name__)


class MahjongEvaluator:
    def __init__(self, generator: MahjongQuestionGenerator):
        self.generator = generator
        self.model_name = generator.model_name

    def evals(self, dataset: List[Dict[str, Any]]) -> pd.DataFrame:
        eval_results: List[EvalResult] = []
        for d in dataset:
            try:
                result = self.generator.generate_question(d["query"])
            except AgentSetupError:
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
            hand_or_error = process_hand_generation(result, d, self.model_name)
            if isinstance(hand_or_error, EvalResult):
                eval_results.append(hand_or_error)
                continue

            # Calculate score and create result
            eval_result = hand_2_result(hand_or_error, d, self.model_name)
            eval_results.append(eval_result)

        return result_to_df(eval_results)


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
