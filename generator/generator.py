from typing import Any, Dict, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.hub import pull
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import ValidationError

from entity.entity import Hand
from exceptions import AgentSetupError, JSONParseError
from llmmj.tools import CalculateMahjongScoreTool
from prompts.prompts import (
    generate_question_prompt_template,
    generate_question_with_tools_prompt_template,
)


class MahjongQuestionGenerator:
    def __init__(
        self, model, use_tools: bool = False, query_template: Optional[str] = None
    ):
        self.model = model
        self.model_name = getattr(
            model, "model_name", getattr(model, "model", "unknown")
        )
        self.parser = JsonOutputParser(pydantic_object=Hand)
        self.use_tools = use_tools

        # Choose the appropriate template based on whether MCP is enabled
        if query_template:
            self.query_template = query_template
        elif use_tools:
            self.query_template = generate_question_with_tools_prompt_template
        else:
            self.query_template = generate_question_prompt_template

        self.tools = []
        self.agent_executor = None

        if use_tools:
            self._setup_react()

    def _setup_react(self):
        """Setup MCP-style tools using LangChain."""
        try:
            # Create tools
            self.tools = [CalculateMahjongScoreTool()]

            # Create agent
            prompt = pull("hwchase17/react")
            agent = create_react_agent(self.model, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate",
            )

        except Exception as e:
            raise AgentSetupError(f"Failed to setup ReAct agent: {e!s}")

    def generate_question(self, query: str) -> Dict[str, Any]:
        """Generate a Mahjong question based on the query."""
        if self.use_tools and self.agent_executor:
            return self._generate_question_with_mcp(query)
        else:
            return self._generate_question_simple(query)

    def _generate_question_simple(self, query: str) -> Dict[str, Any]:
        """Generate question using simple prompt template without MCP tools."""
        prompt = PromptTemplate(
            template=self.query_template,
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        chain = prompt | self.model | self.parser
        try:
            return chain.invoke({"query": query})
        except ValidationError as e:
            raise JSONParseError(
                f"Failed to parse simple generation output as JSON(input): {e!s}"
            )

    def _generate_question_with_mcp(self, query: str) -> Dict[str, Any]:
        # Use agent to generate and verify
        try:
            result = self.agent_executor.invoke({"input": query})
            # Strip markdown formatting before parsing
            output = result["output"]
            if isinstance(output, str):
                # Remove markdown code blocks
                output = (
                    output.replace("```json\n", "")
                    .replace("\n```", "")
                    .replace("```json", "")
                    .replace("```", "")
                )
                output = output.strip()
            return self.parser.parse(output)
        except ValidationError as e:
            raise JSONParseError(
                f"Failed to parse agent output as JSON: {e!s}, result: {result}"
            )
