import logging
from typing import Any, Dict, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.hub import pull
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from entity.entity import Hand
from llmmj.tools import (
    CalculateMahjongScoreTool,
    CheckWinningHandTool,
    ValidateMahjongHandTool,
)
from prompts.prompts import (
    generate_question_prompt_template,
    generate_question_with_tools_prompt_template,
)

logger = logging.getLogger(__name__)


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
            self._setup_mcp_tools()

    def _setup_mcp_tools(self):
        """Setup MCP-style tools using LangChain."""
        try:
            # Create tools
            self.tools = [
                CalculateMahjongScoreTool(),
                # ValidateMahjongHandTool(),
                # CheckWinningHandTool(),
            ]

            # Create agent
            prompt = pull("hwchase17/react")
            agent = create_react_agent(self.model, self.tools, prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate",
            )

            logger.info(
                f"MCP-style tools setup completed. Available tools: {[tool.name for tool in self.tools]}"
            )

        except Exception as e:
            logger.error(f"Failed to setup MCP-style tools: {e}")
            self.use_tools = False
            self.query_template = generate_question_prompt_template

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
        except Exception as e:
            logger.warning(f"Failed to parse simple generation output as JSON: {e}")
            # Try to get raw output and format it
            try:
                simple_chain = prompt | self.model
                raw_output = simple_chain.invoke({"query": query})

                # Extract content from response
                if hasattr(raw_output, "content"):
                    raw_text = raw_output.content
                else:
                    raw_text = str(raw_output)

                # Try to format as JSON
                return self._format_output_as_json(raw_text)
            except Exception as format_error:
                logger.error(
                    f"Failed to format simple generation output: {format_error}"
                )
                raise

    def _generate_question_with_mcp(self, query: str) -> Dict[str, Any]:
        """Generate question using MCP-style tools for verification."""
        enhanced_query = f"""
        {query}
        
        Format Instructions:
        {self.parser.get_format_instructions()}
        
        作った麻雀問題をユーザーに返す前に、必ず以下のツールを使って検証してください：
        
        1. validate_mahjong_hand: 手牌が有効かどうかをチェック
        2. check_winning_hand: 和了形になっているかをチェック  
        3. calculate_mahjong_score: 点数計算が正しいかをチェック
        
        検証で問題が見つかった場合は、修正してから最終的なJSONレスポンスを返してください。
        検証が成功した場合は、そのままJSONレスポンスを返してください。
        """

        try:
            # Use agent to generate and verify
            result = self.agent_executor.invoke({"input": enhanced_query})

            # Try to parse the output
            output = result.get("output", "")
            if isinstance(output, str):
                try:
                    # Try to extract JSON from the output
                    import re

                    # Look for JSON in the output
                    json_match = re.search(r"\{.*\}", output, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        return self.parser.parse(json_str)
                    else:
                        # Try to parse the whole output
                        return self.parser.parse(output)

                except Exception as parse_error:
                    logger.warning(
                        f"Failed to parse agent output as JSON: {parse_error}"
                    )
                    logger.info(f"Raw output: {output}")
                    # Try to format the output as JSON using LLM
                    try:
                        formatted_json = self._format_output_as_json(output)
                        return formatted_json
                    except Exception as format_error:
                        logger.warning(
                            f"Failed to format output as JSON: {format_error}"
                        )
                        # Final fallback to simple generation
                        return self._generate_question_simple(query)
            else:
                return output

        except Exception as e:
            logger.error(f"Failed to generate question with MCP: {e}")
            # Fallback to simple generation
            return self._generate_question_simple(query)

    def _format_output_as_json(self, raw_output: str) -> Dict[str, Any]:
        """Format raw output as JSON using LLM."""
        format_prompt = f"""
以下の麻雀問題の回答を、指定されたJSON形式に整形してください。

元の回答:
{raw_output}

必要なJSON形式:
{self.parser.get_format_instructions()}

重要な注意点:
- 有効なJSONのみを出力してください
- 余計な説明やテキストは含めないでください
- 麻雀牌の表記は正確に保ってください（例: "1m", "2p", "3s", "1z"など）
- 数値は正確に保ってください

JSON:"""

        try:
            response = self.model.invoke(format_prompt)
            # Extract text from response
            if hasattr(response, "content"):
                json_text = response.content
            else:
                json_text = str(response)

            # Try to parse the formatted JSON
            return self.parser.parse(json_text)
        except Exception as e:
            logger.error(f"Failed to format output as JSON: {e}")
            raise
