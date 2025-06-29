#!/usr/bin/env python3
"""Test the enhanced validation functionality in tools.py"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from llmmj.tools import ValidateMahjongHandTool


def test_validation():
    print("🔍 Testing Enhanced Validation Functionality")
    print("=" * 60)

    validator = ValidateMahjongHandTool()

    # Test 1: Valid hand with ankan
    print("\n1. Valid hand with ankan:")
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
    print(f"  Valid: {result['valid']}")
    if result["errors"]:
        print(f"  Errors: {result['errors']}")
    if result["warnings"]:
        print(f"  Warnings: {result['warnings']}")

    # Test 2: Invalid kan (different tiles)
    print("\n2. Invalid kan (different tiles):")
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
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")

    # Test 3: Valid chi
    print("\n3. Valid chi:")
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
    print(f"  Valid: {result['valid']}")
    if result["errors"]:
        print(f"  Errors: {result['errors']}")

    # Test 4: Invalid chi (not consecutive)
    print("\n4. Invalid chi (not consecutive):")
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
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")

    # Test 5: Invalid chi (honor tiles)
    print("\n5. Invalid chi (honor tiles):")
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
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")

    # Test 6: Meld tiles not in hand
    print("\n6. Meld tiles not in hand:")
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
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")

    # Test 7: Too many tiles of same type
    print("\n7. Too many tiles of same type:")
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
    print(f"  Valid: {result['valid']}")
    print(f"  Errors: {result['errors']}")

    print("\n✅ Validation testing completed!")


if __name__ == "__main__":
    test_validation()
