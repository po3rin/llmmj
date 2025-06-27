import logging
from typing import List, Optional

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig
from mahjong.meld import Meld
from mahjong.tile import TilesConverter

from entity.entity import Hand, ScoreResponse

logger = logging.getLogger(__name__)


def convert_tiles_to_136_array(tiles: List[str]) -> List[int]:
    """
    牌の表記を136形式の配列に変換する

    Args:
        tiles: 牌のリスト (例: ["1m", "2m", "3m"])

    Returns:
        List[int]: 136形式の配列
    """
    logger.debug(f"Converting tiles to 136 array: {tiles}")
    man = ""
    pin = ""
    sou = ""
    honors = ""

    for tile in tiles:
        if tile.endswith("m"):
            man += tile[0]
        elif tile.endswith("p"):
            pin += tile[0]
        elif tile.endswith("s"):
            sou += tile[0]
        elif tile.endswith("z"):
            honors += tile[0]

    result = TilesConverter.string_to_136_array(
        man=man, pin=pin, sou=sou, honors=honors
    )
    logger.debug(f"Converted to 136 array: {result}")
    return result


def convert_melds_to_mahjong_format(melds: List[List[str]]) -> List[Meld]:
    """
    鳴きの情報をMahjongライブラリの形式に変換する

    Args:
        melds: 鳴きの情報のリスト

    Returns:
        List[Meld]: Mahjongライブラリの形式の鳴き情報
    """
    logger.debug(f"Converting melds to mahjong format: {melds}")
    result = []
    for meld in melds:
        tiles = convert_tiles_to_136_array(meld)
        # 仮の実装: すべての鳴きをポンとして扱う
        result.append(Meld(meld_type=Meld.PON, tiles=tiles))
    logger.debug(f"Converted melds: {result}")
    return result


def calculate_score(hand: Hand) -> ScoreResponse:
    """
    麻雀の点数を計算する

    Args:
        hand: 手牌の情報
        melds: 鳴きの情報

    Returns:
        ScoreResponse: 点数計算結果
    """
    try:
        logger.info(f"Calculating score for hand: {hand.tiles}")
        calculator = HandCalculator()

        # 手牌を136形式に変換
        tiles = convert_tiles_to_136_array(hand.tiles)
        logger.debug(f"Converted tiles to 136 array: {tiles}")

        # 和了牌を変換
        win_tile = convert_tiles_to_136_array([hand.win_tile])[0]
        logger.debug(f"Win tile: {win_tile}")

        # 鳴きの情報を変換
        mahjong_melds = (
            convert_melds_to_mahjong_format(hand.melds) if hand.melds else []
        )
        logger.debug(f"Converted melds: {mahjong_melds}")

        # ドラ表示牌を変換
        dora_indicators = (
            convert_tiles_to_136_array(hand.dora_indicators)
            if hand.dora_indicators
            else []
        )
        logger.debug(f"Converted dora indicators: {dora_indicators}")

        # 設定を準備
        config = HandConfig(
            is_riichi=hand.is_riichi,
            is_tsumo=hand.is_tsumo,
            is_ippatsu=hand.is_ippatsu,
            is_rinshan=hand.is_rinshan,
            is_chankan=hand.is_chankan,
            is_haitei=hand.is_haitei,
            is_houtei=hand.is_houtei,
            is_daburu_riichi=hand.is_daburu_riichi,
            is_nagashi_mangan=hand.is_nagashi_mangan,
            is_tenhou=hand.is_tenhou,
            is_chiihou=hand.is_chiihou,
            is_open_riichi=hand.is_open_riichi,
            player_wind=hand.player_wind,
            round_wind=hand.round_wind,
            paarenchan=hand.paarenchan,
            kyoutaku_number=hand.kyoutaku_number,
            tsumi_number=hand.tsumi_number,
        )
        logger.debug(f"Hand config: {config.__dict__}")

        # 点数計算
        result = calculator.estimate_hand_value(
            tiles,
            win_tile,
            melds=mahjong_melds,
            dora_indicators=dora_indicators,
            config=config,
        )

        # 結果を変換
        if result is None:
            logger.error("No valid hand found")
            return ScoreResponse(
                han=0, fu=0, score=0, yaku=[], error="No valid hand found"
            )

        return ScoreResponse(
            han=result.han,
            fu=result.fu,
            score=result.cost["main"],
            yaku=[yaku.name for yaku in result.yaku],
            fu_details=result.fu_details,
        )

    except Exception as e:
        logger.error(f"Error during score calculation: {str(e)}", exc_info=True)
        return ScoreResponse(han=0, fu=0, score=0, yaku=result.yaku, error=str(e))


def validate_tiles(tiles: List[str]) -> bool:
    """
    牌の形式が正しいかチェックする

    Args:
        tiles: 牌のリスト

    Returns:
        bool: 正しい形式かどうか
    """
    try:
        logger.debug(f"Validating tiles: {tiles}")
        convert_tiles_to_136_array(tiles)
        return True
    except Exception as e:
        logger.error(f"Invalid tile format: {str(e)}")
        return False


def validate_meld(tiles: List[str], melds: List[List[str]]) -> bool:
    """
    鳴きの形式が正しいかチェックする

    Args:
        tiles: 手牌のリスト
        melds: 鳴きのリストのリスト

    Returns:
        bool: 正しい形式かどうか
    """
    try:
        logger.debug(f"Validating melds: {melds}")
        # 各鳴きを検証
        for meld in melds:
            convert_tiles_to_136_array(meld)
    except Exception as e:
        logger.error(f"Invalid meld format: {str(e)}")
        return False

    # meldsに存在する牌は全てtilesに含まれているべき
    for meld in melds:
        for tile in meld:
            if tile not in tiles:
                logger.error(f"Invalid meld in hand: {meld}")
                return False
    return True
