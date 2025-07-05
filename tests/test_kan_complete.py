"""Complete test suite for kan meld open/closed functionality."""

from entity.entity import Hand, MeldInfo
from llmmj.llmmj import (
    _detect_meld_type,
    calculate_score,
    convert_melds_to_mahjong_format,
)


class TestMeldInfo:
    """Test MeldInfo object creation and behavior."""

    def test_ankan_creation(self):
        """Test ankan (closed kan) creation."""
        ankan = MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False)
        assert ankan.tiles == ["1z", "1z", "1z", "1z"]
        assert ankan.is_open is False

    def test_minkan_creation(self):
        """Test minkan (open kan) creation."""
        minkan = MeldInfo(tiles=["5p", "5p", "5p", "5p"], is_open=True)
        assert minkan.tiles == ["5p", "5p", "5p", "5p"]
        assert minkan.is_open is True

    def test_pon_creation(self):
        """Test pon creation."""
        pon = MeldInfo(tiles=["2s", "2s", "2s"], is_open=True)
        assert pon.tiles == ["2s", "2s", "2s"]
        assert pon.is_open is True


class TestMeldTypeDetection:
    """Test automatic meld type detection."""

    def test_kan_detection(self):
        """Test detection of kan (4 tiles)."""
        assert _detect_meld_type(["1z", "1z", "1z", "1z"]) == "kan"

    def test_pon_detection(self):
        """Test detection of pon (3 identical tiles)."""
        assert _detect_meld_type(["5p", "5p", "5p"]) == "pon"

    def test_chi_detection(self):
        """Test detection of chi (3 consecutive tiles)."""
        assert _detect_meld_type(["1m", "2m", "3m"]) == "chi"


class TestMeldConversion:
    """Test conversion to mahjong library format."""

    def test_ankan_conversion(self):
        """Test ankan conversion."""
        melds = [MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False)]
        converted = convert_melds_to_mahjong_format(melds)

        assert len(converted) == 1
        assert converted[0].type == "kan"
        assert converted[0].opened is False

    def test_minkan_conversion(self):
        """Test minkan conversion."""
        melds = [MeldInfo(tiles=["5p", "5p", "5p", "5p"], is_open=True)]
        converted = convert_melds_to_mahjong_format(melds)

        assert len(converted) == 1
        assert converted[0].type == "kan"
        assert converted[0].opened is True

    def test_pon_conversion(self):
        """Test open pon conversion."""
        melds = [MeldInfo(tiles=["2s", "2s", "2s"], is_open=True)]
        converted = convert_melds_to_mahjong_format(melds)

        assert len(converted) == 1
        assert converted[0].type == "pon"
        assert converted[0].opened is True

    def test_chi_conversion(self):
        """Test chi conversion."""
        melds = [MeldInfo(tiles=["3m", "4m", "5m"], is_open=True)]
        converted = convert_melds_to_mahjong_format(melds)

        assert len(converted) == 1
        assert converted[0].type == "chi"
        assert converted[0].opened is True

    def test_multiple_melds_conversion(self):
        """Test conversion of multiple melds."""
        melds = [
            MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False),
            MeldInfo(tiles=["5p", "5p", "5p", "5p"], is_open=True),
            MeldInfo(tiles=["2s", "2s", "2s"], is_open=True),
            MeldInfo(tiles=["3m", "4m", "5m"], is_open=True),
        ]
        converted = convert_melds_to_mahjong_format(melds)

        assert len(converted) == 4
        assert [m.type for m in converted] == ["kan", "kan", "pon", "chi"]
        assert [m.opened for m in converted] == [False, True, True, True]


class TestHandCreation:
    """Test Hand object creation with various meld types."""

    def test_hand_with_ankan(self):
        """Test hand creation with ankan."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "1z",
                "1z",
                "1z",
                "1z",
            ],
            win_tile="1s",
            melds=[
                MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False),
            ],
            is_tsumo=True,
            player_wind="east",
            round_wind="east",
        )

        assert len(hand.tiles) == 15
        assert len(hand.melds) == 1
        assert hand.melds[0].tiles == ["1z", "1z", "1z", "1z"]
        assert hand.melds[0].is_open is False
        assert hand.win_tile == "1s"

    def test_hand_with_open_pon(self):
        """Test hand creation with open pon."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "5p",
                "5p",
                "5p",
            ],
            win_tile="1s",
            melds=[MeldInfo(tiles=["5p", "5p", "5p"], is_open=True)],
            is_tsumo=True,
        )

        assert len(hand.tiles) == 14
        assert len(hand.melds) == 1
        assert hand.melds[0].tiles == ["5p", "5p", "5p"]
        assert hand.melds[0].is_open is True


class TestAPICompatibility:
    """Test API-style dict format conversion."""

    def test_dict_to_meldinfo_conversion(self):
        """Test converting dict format to MeldInfo objects."""
        api_melds = [
            {"tiles": ["1z", "1z", "1z", "1z"], "is_open": False},
            {"tiles": ["5p", "5p", "5p"], "is_open": True},
        ]

        converted_melds = []
        for meld_dict in api_melds:
            meld_info = MeldInfo(
                tiles=meld_dict["tiles"], is_open=meld_dict.get("is_open", True)
            )
            converted_melds.append(meld_info)

        assert len(converted_melds) == 2
        assert converted_melds[0].tiles == ["1z", "1z", "1z", "1z"]
        assert converted_melds[0].is_open is False
        assert converted_melds[1].tiles == ["5p", "5p", "5p"]
        assert converted_melds[1].is_open is True

    def test_hand_with_api_melds(self):
        """Test creating hand with API-converted melds."""
        api_melds = [
            {"tiles": ["1z", "1z", "1z", "1z"], "is_open": False},
            {"tiles": ["5p", "5p", "5p"], "is_open": True},
        ]

        converted_melds = [
            MeldInfo(tiles=meld["tiles"], is_open=meld.get("is_open", True))
            for meld in api_melds
        ]

        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "1z",
                "1z",
                "1z",
                "1z",
                "5p",
                "5p",
                "5p",
            ],
            win_tile="1s",
            melds=converted_melds,
            is_tsumo=True,
        )

        assert len(hand.melds) == 2
        assert hand.melds[0].is_open is False
        assert hand.melds[1].is_open is True


class TestScoreCalculationIntegration:
    """Test integration with score calculation."""

    def test_score_with_no_melds(self):
        """Test score calculation with no melds."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1p",
                "2p",
                "3p",
                "1s",
                "1s",
            ],
            win_tile="1s",
            melds=None,
            is_tsumo=True,
        )

        result = calculate_score(hand)
        assert hasattr(result, "han")
        assert hasattr(result, "fu")
        assert hasattr(result, "score")

    def test_score_with_open_pon(self):
        """Test score calculation with open pon."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "5p",
                "5p",
                "5p",
            ],
            win_tile="1s",
            melds=[MeldInfo(tiles=["5p", "5p", "5p"], is_open=True)],
            is_tsumo=False,
        )

        result = calculate_score(hand)
        assert hasattr(result, "han")
        assert hasattr(result, "fu")
        assert hasattr(result, "score")

    def test_score_with_ankan(self):
        """Test score calculation with ankan."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "1z",
                "1z",
                "1z",
                "1z",
            ],
            win_tile="1s",
            melds=[MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False)],
            is_tsumo=True,
        )

        result = calculate_score(hand)
        assert hasattr(result, "han")
        assert hasattr(result, "fu")
        assert hasattr(result, "score")

    def test_score_with_minkan(self):
        """Test score calculation with minkan."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7m",
                "8m",
                "9m",
                "1s",
                "1s",
                "5p",
                "5p",
                "5p",
                "5p",
            ],
            win_tile="1s",
            melds=[MeldInfo(tiles=["5p", "5p", "5p", "5p"], is_open=True)],
            is_tsumo=False,
        )

        result = calculate_score(hand)
        assert hasattr(result, "han")
        assert hasattr(result, "fu")
        assert hasattr(result, "score")

    def test_score_with_mixed_melds(self):
        """Test score calculation with mixed melds."""
        hand = Hand(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "1s",
                "1s",
                "2z",
                "2z",
                "2z",
                "2z",
                "5p",
                "5p",
                "5p",
            ],
            win_tile="1s",
            melds=[
                MeldInfo(tiles=["2z", "2z", "2z", "2z"], is_open=False),
                MeldInfo(tiles=["5p", "5p", "5p"], is_open=True),
            ],
            is_tsumo=True,
        )

        result = calculate_score(hand)
        assert hasattr(result, "han")
        assert hasattr(result, "fu")
        assert hasattr(result, "score")


class TestMixedFormatCompatibility:
    """Test mixing different meld formats."""

    def test_mixed_meld_formats(self):
        """Test handling mixed MeldInfo formats."""
        mixed_melds = [
            MeldInfo(tiles=["1z", "1z", "1z", "1z"], is_open=False),
            MeldInfo(tiles=["5p", "5p", "5p"], is_open=True),
            MeldInfo(tiles=["2s", "2s", "2s"], is_open=True),
            MeldInfo(tiles=["3m", "4m", "5m"], is_open=True),
        ]

        converted = convert_melds_to_mahjong_format(mixed_melds)

        assert len(converted) == 4
        assert converted[0].type == "kan" and converted[0].opened is False
        assert converted[1].type == "pon" and converted[1].opened is True
        assert converted[2].type == "pon" and converted[2].opened is True
        assert converted[3].type == "chi" and converted[3].opened is True
