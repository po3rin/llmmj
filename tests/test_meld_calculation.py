import pytest

from tools.calculation import calculate_mahjong_score


class TestMeldCalculationFix:
    """Test mahjong score calculation with dictionary meld format to verify the fix for 'Invalid meld' error"""

    def test_ankan_2_han_60_fu_dict_meld(self):
        """Test ankan example with dictionary meld format that should result in 2 han and 60 fu"""
        result = calculate_mahjong_score(
            tiles=[
                "4m",
                "4m",
                "4m",
                "4m",
                "4z",
                "4z",
                "4z",
                "1p",
                "1p",
                "2s",
                "3s",
                "4s",
                "6s",
                "7s",
                "8s",
            ],
            melds=[{"tiles": ["4m", "4m", "4m", "4m"], "is_open": False}],
            win_tile="7s",
            dora_indicators=["6s"],
            is_riichi=True,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        assert result["han"] == 2
        assert result["fu"] == 60
        assert result["error"] is None
        assert "Riichi" in result["yaku"]
        assert "Dora 1" in result["yaku"]

    def test_no_melds_triplet_example(self):
        """Test example with no melds - should not have meld validation issues"""
        result = calculate_mahjong_score(
            tiles=[
                "5z",
                "5z",
                "5z",
                "1m",
                "1m",
                "1m",
                "9p",
                "9p",
                "2s",
                "3s",
                "4s",
                "6s",
                "7s",
                "8s",
            ],
            melds=[],
            win_tile="7s",
            dora_indicators=["6s"],
            is_riichi=True,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        assert result["han"] == 3
        assert result["fu"] == 50
        assert result["error"] is None
        assert "Riichi" in result["yaku"]
        assert "Yakuhai (haku)" in result["yaku"]

    def test_san_ankou_dict_meld(self):
        """Test example with dictionary meld that results in San Ankou"""
        result = calculate_mahjong_score(
            tiles=[
                "5m",
                "5m",
                "5m",
                "5m",
                "4z",
                "4z",
                "4z",
                "1s",
                "1s",
                "1s",
                "2p",
                "2p",
                "6p",
                "7p",
                "8p",
            ],
            melds=[{"tiles": ["5m", "5m", "5m", "5m"], "is_open": False}],
            win_tile="7p",
            dora_indicators=["6s"],
            is_riichi=True,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        assert result["han"] == 3
        assert result["fu"] == 70
        assert result["error"] is None
        assert "Riichi" in result["yaku"]
        assert "San Ankou" in result["yaku"]

    def test_another_2_han_60_fu_dict_meld(self):
        """Test another ankan example with dictionary meld that should result in 2 han and 60 fu"""
        result = calculate_mahjong_score(
            tiles=[
                "5m",
                "5m",
                "5m",
                "5m",
                "1z",
                "1z",
                "1z",
                "1p",
                "1p",
                "2s",
                "3s",
                "4s",
                "6s",
                "7s",
                "8s",
            ],
            melds=[{"tiles": ["5m", "5m", "5m", "5m"], "is_open": False}],
            win_tile="7s",
            dora_indicators=["6s"],
            is_riichi=True,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        assert result["han"] == 2
        assert result["fu"] == 60
        assert result["error"] is None
        assert "Riichi" in result["yaku"]
        assert "Dora 1" in result["yaku"]

    def test_meld_validation_no_invalid_meld_error(self):
        """Test that dictionary meld format does not trigger 'Invalid meld' error"""
        result = calculate_mahjong_score(
            tiles=[
                "4m",
                "4m",
                "4m",
                "4m",
                "4z",
                "4z",
                "4z",
                "1p",
                "1p",
                "2s",
                "3s",
                "4s",
                "6s",
                "7s",
                "8s",
            ],
            melds=[{"tiles": ["4m", "4m", "4m", "4m"], "is_open": False}],
            win_tile="7s",
            dora_indicators=["6s"],
            is_riichi=True,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        # Should not have "Invalid meld" error
        assert "Invalid meld" not in str(result.get("error", ""))
        assert result["error"] is None

    def test_dict_meld_with_is_open_true(self):
        """Test dictionary meld with is_open=True (open meld) - verify no 'Invalid meld' error"""
        result = calculate_mahjong_score(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7p",
                "8p",
                "9p",
                "1s",
                "1s",
                "5p",
                "5p",
                "5p",
            ],
            melds=[{"tiles": ["5p", "5p", "5p"], "is_open": True}],
            win_tile="1s",
            dora_indicators=["2s"],
            is_riichi=False,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        # Should not have "Invalid meld" error (may have "no_yaku" which is different)
        assert "Invalid meld" not in str(result.get("error", ""))
        # The result should be processed without meld format errors
        assert isinstance(result, dict)

    def test_mixed_meld_formats(self):
        """Test that both dictionary and list formats work - verify no 'Invalid meld' error"""
        # This is just to ensure backward compatibility is maintained
        result = calculate_mahjong_score(
            tiles=[
                "1m",
                "2m",
                "3m",
                "4m",
                "5m",
                "6m",
                "7p",
                "8p",
                "9p",
                "1s",
                "1s",
                "5p",
                "5p",
                "5p",
            ],
            melds=[["5p", "5p", "5p"]],  # Old list format
            win_tile="1s",
            dora_indicators=["2s"],
            is_riichi=False,
            is_tsumo=False,
            player_wind="south",
            round_wind="east",
        )

        # Should not have "Invalid meld" error (may have "no_yaku" which is different)
        assert "Invalid meld" not in str(result.get("error", ""))
        # The result should be processed without meld format errors
        assert isinstance(result, dict)
