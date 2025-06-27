import logging
from typing import Any, Dict, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.hub import pull
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from entity.entity import Hand
from prompts.prompts import (
    generate_question_prompt_template,
    generate_question_with_mcp_prompt_template,
)
from llmmj.tools import CalculateMahjongScoreTool, ValidateMahjongHandTool, CheckWinningHandTool

logger = logging.getLogger(__name__)


class MahjongQuestionGenerator:
    def __init__(
        self, model, use_mcp: bool = False, query_template: Optional[str] = None
    ):
        self.model = model
        self.model_name = getattr(model, "model_name", getattr(model, "model", "unknown"))
        self.parser = JsonOutputParser(pydantic_object=Hand)
        self.use_mcp = use_mcp

        # Choose the appropriate template based on whether MCP is enabled
        if query_template:
            self.query_template = query_template
        elif use_mcp:
            self.query_template = generate_question_with_mcp_prompt_template
        else:
            self.query_template = generate_question_prompt_template

        self.tools = []
        self.agent_executor = None

        if use_mcp:
            self._setup_mcp_tools()

    def _setup_mcp_tools(self):
        """Setup MCP-style tools using LangChain."""
        try:
            # Create tools
            self.tools = [
                CalculateMahjongScoreTool(),
                ValidateMahjongHandTool(),
                CheckWinningHandTool(),
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
                early_stopping_method="generate"
            )
            
            logger.info(f"MCP-style tools setup completed. Available tools: {[tool.name for tool in self.tools]}")
            
        except Exception as e:
            logger.error(f"Failed to setup MCP-style tools: {e}")
            self.use_mcp = False
            self.query_template = generate_question_prompt_template

    def generate_question(self, query: str) -> Dict[str, Any]:
        """Generate a Mahjong question based on the query."""
        if self.use_mcp and self.agent_executor:
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
        return chain.invoke({"query": query})

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
                    import json
                    import re
                    
                    # Look for JSON in the output
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        return self.parser.parse(json_str)
                    else:
                        # Try to parse the whole output
                        return self.parser.parse(output)
                        
                except Exception as parse_error:
                    logger.warning(f"Failed to parse agent output as JSON: {parse_error}")
                    logger.info(f"Raw output: {output}")
                    # Fallback to simple generation
                    return self._generate_question_simple(query)
            else:
                return output

        except Exception as e:
            logger.error(f"Failed to generate question with MCP: {e}")
            # Fallback to simple generation
            return self._generate_question_simple(query)
