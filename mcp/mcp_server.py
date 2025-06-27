import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import mcp
from apimcp.fast_api import ScoreRequest, ScoreResponse
from entity.entity import Hand
from llmmj.llmmj import calculate_score, validate_tiles

logger = logging.getLogger(__name__)

server = mcp.server.fastmcp.FastMCP("mahjong-calculation-mcp")


@server.tool()
def calculate_mahjong_score(
    tiles: list[str],
    win_tile: str,
    melds: list[list[str]] = None,
    dora_indicators: list[str] = None,
    is_riichi: bool = False,
    is_tsumo: bool = False,
    is_ippatsu: bool = False,
    is_rinshan: bool = False,
    is_chankan: bool = False,
    is_haitei: bool = False,
    is_houtei: bool = False,
    is_daburu_riichi: bool = False,
    is_nagashi_mangan: bool = False,
    is_tenhou: bool = False,
    is_chiihou: bool = False,
    is_renhou: bool = False,
    is_open_riichi: bool = False,
    player_wind: str = None,
    round_wind: str = None,
    paarenchan: int = 0,
    kyoutaku_number: int = 0,
    tsumi_number: int = 0,
) -> ScoreResponse:
    """麻雀の点数を計算します。

    Args:
        tiles: 136形式の配列であり和了時の手牌です。14枚になります。例: ["1m", "2m", "3m", "4m", "4m", "5p", "5p", "5p", "7p", "8p", "9p", "1z", "1z", "1z"]
        win_tile: 和了牌です。例: "1m"
        melds: 鳴きの情報を格納する配列です。例: [["1m", "2m", "3m"], ["4s", "4s", "4s"]]
        dora_indicators: ドラ表示牌のリストです。例: ["2m"]
        is_riichi: リーチ宣言済みかどうか
        is_tsumo: 自摸和了かどうか
        is_ippatsu: 一発かどうか
        is_rinshan: 嶺上開花かどうか
        is_chankan: 槍槓かどうか
        is_haitei: 海底摸月かどうか
        is_houtei: 河底撈魚かどうか
        is_daburu_riichi: ダブルリーチかどうか
        is_nagashi_mangan: 流し満貫かどうか
        is_tenhou: 天和かどうか
        is_chiihou: 地和かどうか
        is_renhou: 人和かどうか
        is_open_riichi: オープンリーチかどうか
        player_wind: 自風 (east, south, west, north)
        round_wind: 場風 (east, south, west, north)
        paarenchan: パー連荘の数
        kyoutaku_number: 供託の数 (1000点単位)
        tsumi_number: 積み棒の数 (100点単位)

    Returns:
        ScoreResponse: 点数計算結果
    """
    logger.info(
        f"Received score calculation request: tiles={tiles}, win_tile={win_tile}, melds={melds}"
    )

    # 手牌の形式チェック
    if not validate_tiles(tiles):
        logger.error(f"Invalid tile format in hand: {tiles}")
        raise Exception(detail="Invalid tile format in hand")

    # ドラ表示牌の形式チェック
    if dora_indicators and not validate_tiles(dora_indicators):
        logger.error(f"Invalid tile format in dora indicators: {dora_indicators}")
        raise Exception(detail="Invalid tile format in dora indicators")

    # 鳴きの形式チェック
    if melds:
        for meld in melds:
            if not validate_tiles(meld):
                logger.error(f"Invalid tile format in melds: {meld}")
                raise Exception(detail="Invalid tile format in melds")

    try:
        # HandオブジェクトとScoreRequestオブジェクトを構築
        hand = Hand(
            tiles=tiles,
            win_tile=win_tile,
            melds=melds or [],
            dora_indicators=dora_indicators or [],
            is_riichi=is_riichi,
            is_tsumo=is_tsumo,
            is_ippatsu=is_ippatsu,
            is_rinshan=is_rinshan,
            is_chankan=is_chankan,
            is_haitei=is_haitei,
            is_houtei=is_houtei,
            is_daburu_riichi=is_daburu_riichi,
            is_nagashi_mangan=is_nagashi_mangan,
            is_tenhou=is_tenhou,
            is_chiihou=is_chiihou,
            is_renhou=is_renhou,
            is_open_riichi=is_open_riichi,
            player_wind=player_wind,
            round_wind=round_wind,
            paarenchan=paarenchan,
            kyoutaku_number=kyoutaku_number,
            tsumi_number=tsumi_number,
        )

        request = ScoreRequest(hand=hand)
        result = calculate_score(request)
        logger.info(f"Score calculation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error calculating score: {e}")
        # エラー時もScoreResponseを返す
        return ScoreResponse(han=0, fu=0, score=0, yaku=[], fu_details=[], error=str(e))


@server.tool()
def validate_mahjong_hand(
    tiles: list[str],
    win_tile: str = None,
    melds: list[list[str]] = None,
) -> dict:
    """麻雀の手牌が有効かどうかを検証します。

    Args:
        tiles: 136形式の配列であり和了時の手牌です。例: ["1m", "2m", "3m", "4m", "4m", "5p", "5p", "5p", "7p", "8p", "9p", "1z", "1z", "1z"]
        win_tile: 和了牌です。例: "1m"
        melds: 鳴きの情報を格納する配列です。例: [["1m", "2m", "3m"], ["4s", "4s", "4s"]]

    Returns:
        dict: 検証結果 {"valid": bool, "errors": list[str], "warnings": list[str]}
    """
    errors = []
    warnings = []

    # 手牌の形式チェック
    if not validate_tiles(tiles):
        errors.append("Invalid tile format in hand")

    # 手牌の枚数チェック
    if len(tiles) != 14:
        errors.append(f"Hand should have 14 tiles, but has {len(tiles)} tiles")

    # 和了牌の形式チェック
    if win_tile and not validate_tiles([win_tile]):
        errors.append("Invalid tile format in win_tile")

    # 和了牌が手牌に含まれているかチェック
    if win_tile and win_tile not in tiles:
        errors.append("Win tile is not in the hand")

    # 鳴きの形式チェック
    if melds:
        for i, meld in enumerate(melds):
            if not validate_tiles(meld):
                errors.append(f"Invalid tile format in meld {i}")
            elif len(meld) not in [3, 4]:
                errors.append(f"Meld {i} should have 3 or 4 tiles, but has {len(meld)}")

            # 鳴きの牌が手牌に含まれているかチェック
            for tile in meld:
                if tile not in tiles:
                    errors.append(f"Meld tile {tile} is not in the hand")

    # 牌の重複チェック（各牌は最大4枚まで）
    tile_counts = {}
    for tile in tiles:
        tile_counts[tile] = tile_counts.get(tile, 0) + 1
        if tile_counts[tile] > 4:
            errors.append(f"Tile {tile} appears more than 4 times")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


@server.tool()
def check_winning_hand(
    tiles: list[str],
    win_tile: str,
    melds: list[list[str]] = None,
) -> dict:
    """麻雀の手牌が和了形になっているかどうかをチェックします。

    Args:
        tiles: 136形式の配列であり和了時の手牌です。例: ["1m", "2m", "3m", "4m", "4m", "5p", "5p", "5p", "7p", "8p", "9p", "1z", "1z", "1z"]
        win_tile: 和了牌です。例: "1m"
        melds: 鳴きの情報を格納する配列です。例: [["1m", "2m", "3m"], ["4s", "4s", "4s"]]

    Returns:
        dict: 和了形チェック結果 {"is_winning": bool, "reason": str}
    """
    try:
        # まず基本的な検証を行う
        validation_result = validate_mahjong_hand(tiles, win_tile, melds)
        if not validation_result["valid"]:
            return {
                "is_winning": False,
                "reason": f"Invalid hand: {', '.join(validation_result['errors'])}",
            }

        # 実際に点数計算を試みて、エラーが出なければ和了形とみなす
        result = calculate_mahjong_score(
            tiles=tiles,
            win_tile=win_tile,
            melds=melds or [],
        )

        if result.error:
            return {
                "is_winning": False,
                "reason": f"Not a winning hand: {result.error}",
            }

        return {"is_winning": True, "reason": "Valid winning hand"}

    except Exception as e:
        return {"is_winning": False, "reason": f"Error checking winning hand: {str(e)}"}


@server.tool()
def get_possible_yaku(
    tiles: list[str],
    win_tile: str,
    melds: list[list[str]] = None,
    dora_indicators: list[str] = None,
    is_riichi: bool = False,
    is_tsumo: bool = False,
    player_wind: str = None,
    round_wind: str = None,
) -> dict:
    """指定された手牌で可能な役を取得します。

    Args:
        tiles: 136形式の配列であり和了時の手牌です。
        win_tile: 和了牌です。
        melds: 鳴きの情報を格納する配列です。
        dora_indicators: ドラ表示牌のリストです。
        is_riichi: リーチ宣言済みかどうか
        is_tsumo: 自摸和了かどうか
        player_wind: 自風
        round_wind: 場風

    Returns:
        dict: 可能な役の情報 {"yaku": list, "han": int, "fu": int, "score": int}
    """
    try:
        result = calculate_mahjong_score(
            tiles=tiles,
            win_tile=win_tile,
            melds=melds or [],
            dora_indicators=dora_indicators or [],
            is_riichi=is_riichi,
            is_tsumo=is_tsumo,
            player_wind=player_wind,
            round_wind=round_wind,
        )

        if result.error:
            return {"yaku": [], "han": 0, "fu": 0, "score": 0, "error": result.error}

        return {
            "yaku": result.yaku,
            "han": result.han,
            "fu": result.fu,
            "score": result.score,
            "fu_details": result.fu_details,
        }

    except Exception as e:
        return {"yaku": [], "han": 0, "fu": 0, "score": 0, "error": str(e)}


if __name__ == "__main__":
    server.run(transport="stdio")
