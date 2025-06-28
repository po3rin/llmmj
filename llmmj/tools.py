from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from entity.entity import Hand, ScoreRequest
from llmmj.llmmj import calculate_score, validate_tiles


# MCP-style Tool Implementations
class MahjongScoreInput(BaseModel):
    """Input schema for mahjong score calculation."""
    tiles: List[str] = Field(description="手牌の牌リスト（14枚）")
    win_tile: str = Field(description="和了牌")
    melds: Optional[List[List[str]]] = Field(default=[], description="鳴きの情報")
    dora_indicators: Optional[List[str]] = Field(default=[], description="ドラ表示牌")
    is_riichi: bool = Field(default=False, description="リーチ宣言済みか")
    is_tsumo: bool = Field(default=False, description="自摸和了か")
    player_wind: Optional[str] = Field(default=None, description="自風")
    round_wind: Optional[str] = Field(default=None, description="場風")
    is_ippatsu: bool = Field(default=False, description="一発ツモか")
    is_rinshan: bool = Field(default=False, description="嶺上開花ツモか")
    is_chankan: bool = Field(default=False, description="槍槓ツモか")
    is_haitei: bool = Field(default=False, description="海底摸月ツモか")
    is_houtei: bool = Field(default=False, description="河底撈魚ツモか")
    is_daburu_riichi: bool = Field(default=False, description="ダブル立直宣言か")
    is_nagashi_mangan: bool = Field(default=False, description="流し満貫宣言か")
    is_tenhou: bool = Field(default=False, description="天和か")
    is_chiihou: bool = Field(default=False, description="地和か")
    is_renhou: bool = Field(default=False, description="人和か")


class MahjongValidationInput(BaseModel):
    """Input schema for mahjong hand validation."""
    tiles: List[str] = Field(description="手牌の牌リスト")
    win_tile: Optional[str] = Field(default=None, description="和了牌")
    melds: Optional[List[List[str]]] = Field(default=[], description="鳴きの情報")


class CalculateMahjongScoreTool(BaseTool):
    """Tool for calculating mahjong scores."""
    
    name: str = "calculate_mahjong_score"
    description: str = (
        "麻雀の点数を計算します。手牌、和了牌、鳴き、ドラなどの情報から"
        "翻数、符数、点数を計算し、役の詳細も返します。"
    )
    args_schema: type[BaseModel] = MahjongScoreInput

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        try:
            # Create Hand object with all necessary fields
            hand = Hand(
                tiles=kwargs.get("tiles", []),
                win_tile=kwargs.get("win_tile", ""),
                melds=kwargs.get("melds", []),
                dora_indicators=kwargs.get("dora_indicators", []),
                is_riichi=kwargs.get("is_riichi", False),
                is_tsumo=kwargs.get("is_tsumo", False),
                is_ippatsu=kwargs.get("is_ippatsu", False),
                is_rinshan=kwargs.get("is_rinshan", False),
                is_chankan=kwargs.get("is_chankan", False),
                is_haitei=kwargs.get("is_haitei", False),
                is_houtei=kwargs.get("is_houtei", False),
                is_daburu_riichi=kwargs.get("is_daburu_riichi", False),
                is_nagashi_mangan=kwargs.get("is_nagashi_mangan", False),
                is_tenhou=kwargs.get("is_tenhou", False),
                is_chiihou=kwargs.get("is_chiihou", False),
                is_renhou=kwargs.get("is_renhou", False),
                is_open_riichi=kwargs.get("is_open_riichi", False),
                player_wind=kwargs.get("player_wind"),
                round_wind=kwargs.get("round_wind"),
                paarenchan=kwargs.get("paarenchan", 0),
                kyoutaku_number=kwargs.get("kyoutaku_number", 0),
                tsumi_number=kwargs.get("tsumi_number", 0),
            )
            
            # Calculate score
            request = ScoreRequest(hand=hand)
            result = calculate_score(request)
            
            print(f"tools result: {result}")
            
            return {
                "han": result.han,
                "fu": result.fu, 
                "score": result.score,
                "yaku": result.yaku,
                "fu_details": result.fu_details,
                "error": result.error
            }
            
        except Exception as e:
            return {
                "han": 0,
                "fu": 0,
                "score": 0,
                "yaku": [],
                "fu_details": [],
                "error": str(e)
            }


class ValidateMahjongHandTool(BaseTool):
    """Tool for validating mahjong hands."""
    
    name: str = "validate_mahjong_hand"
    description: str = (
        "麻雀の手牌が有効かどうかを検証します。牌の形式、枚数、"
        "重複などをチェックして問題があれば報告します。"
    )
    args_schema: type[BaseModel] = MahjongValidationInput

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        tiles = kwargs.get("tiles", [])
        win_tile = kwargs.get("win_tile")
        melds = kwargs.get("melds", [])
        
        errors = []
        warnings = []
        
        # Basic validation
        if not validate_tiles(tiles):
            errors.append("Invalid tile format in hand")
        
        if len(tiles) != 14:
            errors.append(f"Hand should have 14 tiles, but has {len(tiles)} tiles")
        
        if win_tile and not validate_tiles([win_tile]):
            errors.append("Invalid tile format in win_tile")
        
        if win_tile and win_tile not in tiles:
            errors.append("Win tile is not in the hand")
        
        # Validate melds
        if melds:
            for i, meld in enumerate(melds):
                if not validate_tiles(meld):
                    errors.append(f"Invalid tile format in meld {i}")
                elif len(meld) not in [3, 4]:
                    errors.append(f"Meld {i} should have 3 or 4 tiles, but has {len(meld)}")
        
        # Check tile counts
        tile_counts = {}
        for tile in tiles:
            tile_counts[tile] = tile_counts.get(tile, 0) + 1
            if tile_counts[tile] > 4:
                errors.append(f"Tile {tile} appears more than 4 times")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


class CheckWinningHandTool(BaseTool):
    """Tool for checking if a hand is in winning form."""
    
    name: str = "check_winning_hand"
    description: str = (
        "麻雀の手牌が和了形になっているかどうかをチェックします。"
        "実際に点数計算を試みて、エラーが出なければ和了形とみなします。"
    )
    args_schema: type[BaseModel] = MahjongValidationInput

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        try:
            # First validate
            validator = ValidateMahjongHandTool()
            validation = validator._run(**kwargs)
            
            if not validation["valid"]:
                return {
                    "is_winning": False,
                    "reason": f"Invalid hand: {', '.join(validation['errors'])}"
                }
            
            # Then try to calculate score
            calculator = CalculateMahjongScoreTool()
            score_result = calculator._run(**kwargs)
            
            if score_result.get("error"):
                return {
                    "is_winning": False,
                    "reason": f"Not a winning hand: {score_result['error']}"
                }
            
            return {
                "is_winning": True,
                "reason": "Valid winning hand",
                "score_info": {
                    "han": score_result["han"],
                    "fu": score_result["fu"],
                    "score": score_result["score"],
                    "yaku": score_result["yaku"]
                }
            }
            
        except Exception as e:
            return {
                "is_winning": False,
                "reason": f"Error checking winning hand: {str(e)}"
            }
