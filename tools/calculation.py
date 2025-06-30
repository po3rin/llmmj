import json
import logging
from typing import Any, Dict, List, Optional

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from pydantic import ValidationError

from entity.entity import Hand, MeldInfo
from llmmj.llmmj import (
    convert_melds_to_mahjong_format,
    convert_tiles_to_136_array,
    validate_meld,
    validate_tiles,
)

logging.basicConfig(level=logging.INFO)


def calculate_mahjong_score(
    tiles: List[str],
    win_tile: str,
    melds: Optional[List[Dict[str, Any]]],
    dora_indicators: Optional[List[str]],
    is_riichi: bool,
    is_tsumo: bool,
    player_wind: str,
    round_wind: str,
) -> dict:
    """Calculate mahjong score.

    Args:
        tiles (str): Array in 136 format representing the winning hand. Important: Must include all tiles in the hand, including those specified in melds. Example: For a hand with 10 tiles + 4 ankan tiles + 1 winning tile, specify all 15 tiles like tiles=['1m', '2m', '3m', '4m', '4m', '5p', '5p', '5p', '7p', '8p', '1z', '1z', '1z', '1z', '1s'].

        melds list[MeldInfo] format: MeldInfo(tiles=['1z', '1z', '1z', '1z'], is_open=False)
                - tiles: Meld tiles (136 format). These tiles must also be included in the tiles field.
                - is_open: True=open meld (minkan, pon, chi), False=closed meld (ankan)

        win_tile (str): The winning tile

        dora_indicators (list[str]): Dora indicator tiles

        is_riichi (bool): Whether riichi is declared. Cannot declare riichi after calling melds, so must be False if melds is not None.

        is_tsumo (bool): Whether it's a tsumo win

        player_wind (str): Player's wind (east, south, west, north)

        round_wind (str): Round wind (east, south, west, north)

    Returns:
        dict: Score calculation result
    """
    logging.info("hello calculate_mahjong_score!!!")

    check_hand_validity_result = check_hand_validity(tiles, melds)
    if check_hand_validity_result["status"] == "error":
        return check_hand_validity_result

    # 鳴きの情報を変換
    try:
        # Convert dict melds to MeldInfo objects
        if melds:
            converted_melds = []
            for meld in melds:
                if not isinstance(meld, dict) or "tiles" not in meld:
                    return {
                        "status": "error",
                        "error": "melds must be in MeldInfo format: {'tiles': [...], 'is_open': bool}",
                    }
                # Convert dict to MeldInfo
                converted_melds.append(
                    MeldInfo(tiles=meld["tiles"], is_open=meld.get("is_open", True))
                )
            mahjong_melds = convert_melds_to_mahjong_format(converted_melds)
        else:
            mahjong_melds = []
    except Exception as e:
        return {"status": "error", "error": f"Invalid melds: {e!s}"}

    # 手牌を136形式に変換（全ての牌を含める）
    try:
        tiles = convert_tiles_to_136_array(tiles)
    except Exception as e:
        return {"status": "error", "error": f"Invalid tiles: {e!s}"}

    # 和了牌を変換
    try:
        win_tile = convert_tiles_to_136_array([win_tile])[0]
    except Exception as e:
        return {"status": "error", "error": f"Invalid win_tile: {e!s}"}

    # ドラ表示牌を変換
    try:
        dora_indicators = (
            convert_tiles_to_136_array(dora_indicators) if dora_indicators else []
        )
    except Exception as e:
        return {"status": "error", "error": f"Invalid dora_indicators: {e!s}"}

    # 設定を準備
    config = HandConfig(
        is_riichi=is_riichi,
        is_tsumo=is_tsumo,
        player_wind=player_wind,
        round_wind=round_wind,
    )

    # 点数計算
    try:
        calculator = HandCalculator()
        result = calculator.estimate_hand_value(
            tiles,
            win_tile,
            melds=mahjong_melds,
            dora_indicators=dora_indicators,
            config=config,
        )
    except Exception as e:
        return {"status": "error", "error": f"Invalid result: {e!s}"}

    # HandResponseオブジェクトをdictに変換
    return {
        "han": result.han,
        "fu": result.fu,
        "cost": result.cost,
        "yaku": [str(yaku) for yaku in result.yaku] if result.yaku else [],
        "fu_details": result.fu_details,
        "error": result.error,
    }


def check_hand_validity(
    tiles: List[str],
    melds: Optional[List[Dict[str, Any]]],
) -> dict:
    """Check if the hand & melds is valid.

    Args:
        tiles (str): Array in 136 format representing the winning hand. Important: Must include all tiles in the hand, including those specified in melds. Example: For a hand with 10 tiles + 4 ankan tiles + 1 winning tile, specify all 15 tiles like tiles=['1m', '2m', '3m', '4m', '4m', '5p', '5p', '5p', '7p', '8p', '1z', '1z', '1z', '1z', '1s'].

        melds list[MeldInfo] format: {'tiles': [...], 'is_open': bool}
                - tiles: Meld tiles (136 format). These tiles must also be included in the tiles field.
                - is_open: True=open meld (minkan, pon, chi), False=closed meld (ankan)

    Returns:
        dict: Hand validity check result
    """
    logging.info("hello check_hand_validity!!!")

    if melds:
        # Convert dict melds to MeldInfo for validation
        converted_melds = []
        for meld in melds:
            if not isinstance(meld, dict) or "tiles" not in meld:
                return {
                    "status": "error",
                    "error": "melds must be in MeldInfo format: {'tiles': [...], 'is_open': bool}",
                }
            converted_melds.append(
                MeldInfo(tiles=meld["tiles"], is_open=meld.get("is_open", True))
            )

        if not validate_meld(tiles, converted_melds):
            return {"status": "error", "error": "Invalid meld"}

    if not validate_tiles(tiles):
        return {"status": "error", "error": "Invalid tiles"}

    return {"status": "success"}


def final_output_message_check(message: str) -> dict:
    """Finally, check that the message format returned to the user is correct. It must be returned in the following JSON format.

    {
        "tiles": list[str],
        "melds": list[dict[list[str], str]] or list[list[str]],
        "win_tile": str,
        "dora_indicators": list[str],
        "is_riichi": bool,
        "is_tsumo": bool,
        "player_wind": str,
        "round_wind": str
    }

    Args:
        message (str): The message to check

    Returns:
        dict: Message validity check result
    """
    logging.info("hello final_output_message_check!!!")

    try:
        json.loads(message)
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON format: {e!s}"}

    try:
        Hand.model_validate_json(message)
    except ValidationError as e:
        return {"status": "error", "error": f"Invalid message format: {e!s}"}

    return {"status": "success"}
