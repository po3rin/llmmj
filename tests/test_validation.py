"""Test the enhanced validation functionality in tools.py"""

import pytest

from llmmj.tools import ValidateMahjongHandTool


@pytest.fixture
def validator():
    """Create ValidateMahjongHandTool instance."""
    return ValidateMahjongHandTool()


def test_valid_hand_with_ankan(validator):
    """Test validation of a valid hand with ankan."""
    result = validator._run(
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
            "1z",
            "1z",
            "1z",
            "1z",
            "1s",
        ],
        win_tile="1s",
        melds=[{"tiles": ["1z", "1z", "1z", "1z"], "is_open": False}],
    )

    assert result["valid"] is True
    assert not result["errors"]
    assert not result["warnings"]


def test_invalid_kan_different_tiles(validator):
    """Test validation of invalid kan with different tiles."""
    result = validator._run(
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
            "1z",
            "2z",
            "3z",
            "4z",
            "1s",
        ],
        win_tile="1s",
        melds=[{"tiles": ["1z", "2z", "3z", "4z"], "is_open": False}],
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("identical tiles" in error for error in result["errors"])


def test_valid_chi(validator):
    """Test validation of a valid chi."""
    result = validator._run(
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
            "2s",
            "3s",
            "5p",
            "5p",
            "5p",
        ],
        win_tile="5p",
        melds=[{"tiles": ["1s", "2s", "3s"], "is_open": True}],
    )

    assert result["valid"] is True
    assert not result["errors"]


def test_invalid_chi_not_consecutive(validator):
    """Test validation of invalid chi with non-consecutive tiles."""
    result = validator._run(
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
            "3s",
            "5s",
            "5p",
            "5p",
            "5p",
        ],
        win_tile="5p",
        melds=[{"tiles": ["1s", "3s", "5s"], "is_open": True}],
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("neither a valid pon nor chi" in error for error in result["errors"])


def test_invalid_chi_honor_tiles(validator):
    """Test validation of invalid chi with honor tiles."""
    result = validator._run(
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
            "1z",
            "2z",
            "3z",
            "5p",
            "5p",
        ],
        win_tile="5p",
        melds=[{"tiles": ["1z", "2z", "3z"], "is_open": True}],
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("neither a valid pon nor chi" in error for error in result["errors"])


def test_meld_tiles_not_in_hand(validator):
    """Test validation when meld tiles are not in hand."""
    result = validator._run(
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
            "5p",
            "5p",
            "5p",
            "5p",
        ],
        win_tile="1s",
        melds=[{"tiles": ["1z", "1z", "1z", "1z"], "is_open": False}],
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("not present in hand tiles" in error for error in result["errors"])


def test_too_many_tiles_of_same_type(validator):
    """Test validation with too many tiles of the same type."""
    result = validator._run(
        tiles=[
            "1m",
            "1m",
            "1m",
            "1m",
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
        ],
        win_tile="1s",
        melds=[],
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("appears more than 4 times" in error for error in result["errors"])
