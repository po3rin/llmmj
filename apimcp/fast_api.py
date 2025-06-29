import logging
import sys
from typing import Dict

from fastapi import FastAPI, HTTPException

from entity.entity import ScoreRequest, ScoreResponse
from llmmj.llmmj import calculate_score, validate_tiles

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

    # 手牌の形式チェック
    if not validate_tiles(request.hand.tiles):
        logger.error(f"Invalid tile format in hand: {request.hand.tiles}")
        raise HTTPException(status_code=400, detail="Invalid tile format in hand")

    # ドラ表示牌の形式チェック
    if request.hand.dora_indicators and not validate_tiles(
        request.hand.dora_indicators
    ):
        logger.error(
            f"Invalid tile format in dora indicators: {request.hand.dora_indicators}"
        )
        raise HTTPException(
            status_code=400, detail="Invalid tile format in dora indicators"
        )

    # 鳴きの形式チェック
    if request.hand.melds:
        for meld in request.hand.melds:
            meld_tiles = meld.tiles if hasattr(meld, "tiles") else meld
            if not validate_tiles(meld_tiles):
                logger.error(f"Invalid tile format in melds: {meld_tiles}")
                raise HTTPException(
                    status_code=400, detail="Invalid tile format in melds"
                )

    # 点数計算
    result = calculate_score(request.hand)

    # エラーがある場合は400エラーを返す
    if result.error:
        logger.error(f"Error during score calculation: {result.error}")
        raise HTTPException(status_code=400, detail=result.error)

    logger.info(f"Score calculation result: {result}")
    return result


@app.get("/health", operation_id="health")
async def health_check() -> Dict[str, str]:
    """
    サーバーの状態を確認する

    Returns:
        Dict[str, str]: サーバーの状態
    """
    logger.info("Health check requested")
    return {"status": "ok"}
