import os

rule_path = os.path.join(os.path.dirname(__file__), "../sources/rule_en.md")
with open(rule_path, "r") as f:
    rule_str = f.read()

cot_path = os.path.join(os.path.dirname(__file__), "../sources/cot_en.md")
with open(cot_path, "r") as f:
    cot_str = f.read()

tile_notation_str = """
## Tile Notation
Mahjong hands are represented in 136 format. Man tiles are denoted by m, pin tiles by p, sou tiles by s, and honor tiles by z. Each tile has 4 copies.
1-man:1m, 2-man:2m, 3-man:3m, 4-man:4m, 5-man:5m, 6-man:6m, 7-man:7m, 8-man:8m, 9-man:9m
1-pin:1p, 2-pin:2p, 3-pin:3p, 4-pin:4p, 5-pin:5p, 6-pin:6p, 7-pin:7p, 8-pin:8p, 9-pin:9p
1-sou:1s, 2-sou:2s, 3-sou:3s, 4-sou:4s, 5-sou:5s, 6-sou:6s, 7-sou:7s, 8-sou:8s, 9-sou:9s
East:1z, South:2z, West:3z, North:4z, White:5z, Green:6z, Red:7z
"""

required_json_format_str = """
## **Required JSON Format**
    - The message must be in the following JSON format:
        {{
            "tiles": list[str],
            "melds": list[MeldInfo],
            "win_tile": str,
            "dora_indicators": list[str],
            "is_riichi": bool,
            "is_tsumo": bool,
            "player_wind": str,
            "round_wind": str
        }}
    - tiles: list[str]: Array in 136 format representing the winning hand. Important: Must include all tiles in the hand, including those specified in melds. Example: For a hand with 10 tiles + 4 ankan tiles + 1 winning tile, specify all 15 tiles like tiles=['1m', '2m', '3m', '4m', '4m', '5p', '5p', '5p', '7p', '8p', '1z', '1z', '1z', '1z', '1s'].
    - melds: list[MeldInfo]: Meld information. MeldInfo format only: [{{"tiles": ["1z", "1z", "1z", "1z"], "is_open": false}}]
        - tiles: Meld tiles (136 format). These tiles must also be included in the tiles field.
        - is_open: true=open meld (minkan, pon, chi), false=closed meld (ankan)
    - win_tile (str): The winning tile
    - dora_indicators (list[str]): Dora indicator tiles
    - is_riichi (bool): Whether riichi is declared. Cannot declare riichi after calling melds, so must be False if melds is not None.
    - is_tsumo (bool): Whether it's a tsumo win
    - player_wind (str): Player's wind (east, south, west, north)
    - round_wind (str): Round wind (east, south, west, north)
"""
