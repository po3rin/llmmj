from typing import Optional

from pydantic import BaseModel, Field

from entity.entity import Hand


class EvalResult(BaseModel):
    model: str = Field("unknown", description="モデル名")
    correct: bool = Field(..., description="正解かどうか")
    is_error: bool = Field(..., description="エラーで処理が停止したかどうか")
    error_type: Optional[str] = Field(None, description="エラーの種類")
    reason: str = Field(..., description="理由")
    hand: Hand = Field(..., description="手牌")
    got_answer_han: Optional[int] = Field(None, description="得られた答えの翻数")
    got_answer_fu: Optional[int] = Field(None, description="得られた答えの符数")
    expected_han: int = Field(..., description="期待する答えの翻数")
    expected_fu: int = Field(..., description="期待する答えの符数")
