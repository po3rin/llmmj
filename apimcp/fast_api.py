import logging
import sys
from typing import Dict

from fastapi import FastAPI, HTTPException

from entity.entity import ScoreRequest, ScoreResponse
from llmmj.llmmj import calculate_score, validate_hand

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("api.log")],
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Mahjong Calculation Server",
    description="麻雀の点数計算を行うAPIサーバー",
    version="1.0.0",
    base_url="http://localhost:8000",
)


@app.post("/calculate", operation_id="calculate", response_model=ScoreResponse)
async def calculate(request: ScoreRequest) -> ScoreResponse:
    """
    麻雀の点数を計算する

    Args:
        request: 点数計算リクエスト

    Returns:
        ScoreResponse: 点数計算結果
    """
    logger.info(f"Received score calculation request: {request}")

    # Use centralized validation
    try:
        validate_hand(request.hand)
    except ValueError as e:
        logger.error(f"Hand validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    # 点数計算
    result = calculate_score(request.hand)

    # エラーがある場合は400エラーを返す
    if result.error:
        logger.error(
            f"Error during score calculation: {result.error}, result: {result}"
        )
        raise HTTPException(status_code=400, detail=result.error)

    return result


@app.get("/health", operation_id="health")
async def health_check() -> Dict[str, str]:
    """
    サーバーの状態を確認する

    Returns:
        Dict[str, str]: サーバーの状態
    """
    return {"status": "ok"}
