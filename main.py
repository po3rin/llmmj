import logging

from fastapi_mcp import FastApiMCP

from api.fast_api import app

logger = logging.getLogger(__name__)

mcp = FastApiMCP(
    app,
    name="Mahjong Calculation Protocol (MCP) Server",
    description="麻雀の点数計算を行うAPIサーバー。",
    describe_all_responses=True,
    describe_full_response_schema=True
)

# Mount the MCP server directly to your FastAPI app
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MCP server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
