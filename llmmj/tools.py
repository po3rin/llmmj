from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from entity.entity import Hand, MeldInfo, ScoreRequest
from llmmj.llmmj import calculate_score, validate_tiles


def _is_valid_chi(sorted_tiles: List[str]) -> bool:
    """Check if 3 tiles form a valid chi (consecutive sequence)."""
    if len(sorted_tiles) != 3:
        return False

    # Only number tiles can form chi (not honor tiles)
    suits = [tile[-1] for tile in sorted_tiles]
    if not all(suit in "mps" for suit in suits):
        return False

    # All tiles must be from the same suit
    if not all(suit == suits[0] for suit in suits):
        return False

    # Check if numbers are consecutive
    numbers = [int(tile[0]) for tile in sorted_tiles]
    return numbers[1] == numbers[0] + 1 and numbers[2] == numbers[1] + 1


# MCP-style Tool Implementations
class MahjongScoreInput(BaseModel):
    """Input schema for mahjong score calculation."""

    tiles: List[str] = Field(
        description="List of hand tiles. Important: Must include all tiles in the hand, including those specified in melds. Example: For a hand with 10 tiles + 4 ankan tiles + 1 winning tile, specify all 15 tiles."
    )
    win_tile: str = Field(description="The winning tile")
    melds: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="Meld information. MeldInfo format only: {'tiles': [...], 'is_open': bool}. tiles: List of tiles in the meld (136 format). is_open: true=open meld (minkan, pon, chi), false=closed meld (ankan). Important: Tiles specified in melds must also be included in the tiles field.",
    )
    dora_indicators: Optional[List[str]] = Field(
        default=[], description="Dora indicator tiles"
    )
    is_riichi: bool = Field(default=False, description="Whether riichi is declared")
    is_tsumo: bool = Field(default=False, description="Whether it's a tsumo win")
    player_wind: Optional[str] = Field(default=None, description="Player's wind")
    round_wind: Optional[str] = Field(default=None, description="Round wind")
    is_ippatsu: bool = Field(
        default=False, description="Whether it's ippatsu (one-shot)"
    )
    is_rinshan: bool = Field(
        default=False, description="Whether it's rinshan kaihou (dead wall draw)"
    )
    is_chankan: bool = Field(
        default=False, description="Whether it's chankan (robbing a kan)"
    )
    is_haitei: bool = Field(
        default=False, description="Whether it's haitei raoyue (last tile from wall)"
    )
    is_houtei: bool = Field(
        default=False, description="Whether it's houtei raoyui (last tile from discard)"
    )
    is_daburu_riichi: bool = Field(
        default=False, description="Whether it's double riichi"
    )
    is_nagashi_mangan: bool = Field(
        default=False, description="Whether it's nagashi mangan (discard mangan)"
    )
    is_tenhou: bool = Field(
        default=False, description="Whether it's tenhou (heavenly hand)"
    )
    is_chiihou: bool = Field(
        default=False, description="Whether it's chiihou (earthly hand)"
    )
    is_renhou: bool = Field(
        default=False, description="Whether it's renhou (human hand)"
    )
    is_open_riichi: bool = Field(default=False, description="Whether it's open riichi")
    paarenchan: int = Field(
        default=0, description="Number of paarenchan (repeated draws)"
    )
    kyoutaku_number: int = Field(
        default=0, description="Number of kyoutaku (deposits) in 1000-point units"
    )
    tsumi_number: int = Field(
        default=0, description="Number of tsumi (accumulated) in 100-point units"
    )


class MahjongValidationInput(BaseModel):
    """Input schema for mahjong hand validation."""

    tiles: List[str] = Field(description="手牌の牌リスト")
    win_tile: Optional[str] = Field(default=None, description="和了牌")
    melds: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="鳴きの情報。MeldInfo形式のみ: {'tiles': [...], 'is_open': bool}。tiles: 鳴きの牌（136形式）。is_open: true=明刻（ミンカン、ポン、チー）、false=暗刻（アンカン）。重要: meldsで指定した牌は、tilesフィールドにも重複して含める必要があります。",
    )


class CalculateMahjongScoreTool(BaseTool):
    """Tool for calculating mahjong scores."""

    name: str = "calculate_mahjong_score"
    description: str = (
        "Calculate mahjong score. Computes han, fu, and points from hand tiles, "
        "winning tile, melds, dora, and other information, and returns detailed yaku information."
    )
    args_schema: type[BaseModel] = MahjongScoreInput

    def _run(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool."""
        try:
            # Convert melds to proper format
            melds = kwargs.get("melds", [])
            converted_melds = []
            for meld in melds:
                if isinstance(meld, dict) and "tiles" in meld:
                    converted_melds.append(
                        MeldInfo(tiles=meld["tiles"], is_open=meld.get("is_open", True))
                    )
                else:
                    converted_melds.append(meld)

            # Create Hand object with all necessary fields
            hand = Hand(
                tiles=kwargs.get("tiles", []),
                win_tile=kwargs.get("win_tile", ""),
                melds=converted_melds,
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
                "error": result.error,
            }

        except Exception as e:
            return {
                "han": 0,
                "fu": 0,
                "score": 0,
                "yaku": [],
                "fu_details": [],
                "error": str(e),
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
        # Handle case where input is passed as a JSON string
        if len(kwargs) == 1 and "tiles" in str(list(kwargs.values())[0]):
            try:
                import json

                json_str = list(kwargs.values())[0]
                if isinstance(json_str, str):
                    parsed_input = json.loads(json_str)
                    kwargs = parsed_input
            except:
                pass
        tiles = kwargs.get("tiles", [])
        win_tile = kwargs.get("win_tile")
        melds = kwargs.get("melds", [])

        errors = []
        warnings = []

        # Basic validation
        if not validate_tiles(tiles):
            errors.append("Invalid tile format in hand")

        if len(tiles) < 14:
            errors.append(
                f"Hand should have at least 14 tiles, but has {len(tiles)} tiles"
            )

        if win_tile and not validate_tiles([win_tile]):
            errors.append("Invalid tile format in win_tile")

        if win_tile and win_tile not in tiles:
            errors.append("Win tile is not in the hand")

        # Validate melds
        meld_tiles = []
        if melds:
            for i, meld in enumerate(melds):
                if isinstance(meld, dict):
                    meld_tiles_list = meld.get("tiles", [])
                else:
                    meld_tiles_list = meld

                if not validate_tiles(meld_tiles_list):
                    errors.append(f"Invalid tile format in meld {i}")
                elif len(meld_tiles_list) not in [3, 4]:
                    errors.append(
                        f"Meld {i} should have 3 or 4 tiles, but has {len(meld_tiles_list)}"
                    )
                else:
                    # Check if meld is valid (same tiles for pon/kan, consecutive for chi)
                    if len(meld_tiles_list) == 4:
                        # Kan: all 4 tiles should be the same
                        if not all(
                            tile == meld_tiles_list[0] for tile in meld_tiles_list
                        ):
                            errors.append(f"Kan meld {i} should have 4 identical tiles")
                    elif len(meld_tiles_list) == 3:
                        sorted_meld = sorted(meld_tiles_list)
                        if sorted_meld[0] == sorted_meld[1] == sorted_meld[2]:
                            # Pon: all 3 tiles should be the same
                            pass
                        else:
                            # Chi: should be consecutive
                            if not _is_valid_chi(sorted_meld):
                                errors.append(
                                    f"Meld {i} is neither a valid pon nor chi"
                                )

                    meld_tiles.extend(meld_tiles_list)

        # Check if meld tiles are all present in hand tiles
        for meld_tile in meld_tiles:
            if meld_tile not in tiles:
                errors.append(f"Meld tile {meld_tile} is not present in hand tiles")

        # Check tile counts
        tile_counts = {}
        for tile in tiles:
            tile_counts[tile] = tile_counts.get(tile, 0) + 1
            if tile_counts[tile] > 4:
                errors.append(f"Tile {tile} appears more than 4 times")

        # Check total tile count consistency
        kan_count = 0
        for meld in melds:
            meld_tiles_list = meld.get("tiles", []) if isinstance(meld, dict) else meld
            if len(meld_tiles_list) == 4:
                kan_count += 1

        expected_tiles = 14 + kan_count
        if len(tiles) != expected_tiles:
            warnings.append(
                f"Expected {expected_tiles} tiles (14 + {kan_count} kan tiles), but got {len(tiles)} tiles"
            )

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


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
                    "reason": f"Invalid hand: {', '.join(validation['errors'])}",
                }

            # Then try to calculate score
            calculator = CalculateMahjongScoreTool()
            score_result = calculator._run(**kwargs)

            if score_result.get("error"):
                return {
                    "is_winning": False,
                    "reason": f"Not a winning hand: {score_result['error']}",
                }

            return {
                "is_winning": True,
                "reason": "Valid winning hand",
                "score_info": {
                    "han": score_result["han"],
                    "fu": score_result["fu"],
                    "score": score_result["score"],
                    "yaku": score_result["yaku"],
                },
            }

        except Exception as e:
            return {
                "is_winning": False,
                "reason": f"Error checking winning hand: {str(e)}",
            }
