from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Hand(BaseModel):
    tiles: List[str] = Field(
        ...,
        description="136形式の配列であり和了時の手牌です。14枚になります。例: ['1m', '2m', '3m', '4m', '4m', '5p', '5p', '5p', '7p', '8p', '9p', '1z', '1z', '1z']",
    )
    melds: Optional[List[List[str]]] = Field(
        None,
        description="鳴きの情報。鳴きは136形式の配列であり、それらが配列になっています。例: [['1m', '2m', '3m'], ['4m', '5m', '6m']]",
    )
    win_tile: str = Field(..., description="和了牌。例: '1m'")
    dora_indicators: Optional[List[str]] = Field(None, description="ドラ表示牌のリスト")
    is_riichi: bool = Field(
        False,
        description="リーチ宣言済みかどうか。鳴くとリーチができません。つまりmeldsがNoneでない場合は必ずFalseです。",
    )
    is_tsumo: bool = Field(False, description="自摸和了かどうか")
    is_ippatsu: bool = Field(False, description="一発かどうか")
    is_rinshan: bool = Field(False, description="嶺上開花かどうか")
    is_chankan: bool = Field(False, description="槍槓かどうか")
    is_haitei: bool = Field(False, description="海底摸月かどうか")
    is_houtei: bool = Field(False, description="河底撈魚かどうか")
    is_daburu_riichi: bool = Field(False, description="ダブルリーチかどうか")
    is_nagashi_mangan: bool = Field(False, description="流し満貫かどうか")
    is_tenhou: bool = Field(False, description="天和かどうか")
    is_chiihou: bool = Field(False, description="地和かどうか")
    is_renhou: bool = Field(False, description="人和かどうか")
    is_open_riichi: bool = Field(False, description="オープンリーチかどうか")
    player_wind: Optional[str] = Field(
        None, description="自風 (east, south, west, north)"
    )
    round_wind: Optional[str] = Field(
        None, description="場風 (east, south, west, north)"
    )
    paarenchan: int = Field(0, description="パー連荘の数")
    kyoutaku_number: int = Field(0, description="供託の数 (1000点単位)")
    tsumi_number: int = Field(0, description="積み棒の数 (100点単位)")


class ScoreRequest(BaseModel):
    hand: Hand


class ScoreResponse(BaseModel):
    han: int = Field(..., description="飜数")
    fu: int = Field(..., description="符数")
    score: int = Field(..., description="点数")
    yaku: List[str] = Field(..., description="役のリスト")
    fu_details: List[Dict[str, Any]] = Field(..., description="符の詳細")
    error: Optional[str] = Field(None, description="エラーメッセージ")
