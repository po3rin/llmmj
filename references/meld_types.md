# Mahjong Library Meld Types

The `mahjong` library provides a `Meld` class with the following meld type constants:

## Available Meld Types

1. **Meld.CHI** = "chi"
   - Represents a chow (チー) - a sequence of three consecutive tiles from the same suit
   - Example: 1m-2m-3m, 5p-6p-7p, 7s-8s-9s

2. **Meld.PON** = "pon"
   - Represents a pung (ポン) - a set of three identical tiles
   - Example: 3p-3p-3p, 5z-5z-5z

3. **Meld.KAN** = "kan"
   - Represents a kong (カン) - a set of four identical tiles
   - Can be either open (明槓/minkan) or closed (暗槓/ankan)

4. **Meld.SHOUMINKAN** = "shouminkan"
   - Represents a small added kan (小明槓)
   - This is when you add a fourth tile to an existing PON to make a KAN

5. **Meld.NUKI** = "nuki"
   - Represents a nuki dora (抜きドラ)
   - Used in some rule variations where certain tiles can be set aside as bonus tiles

## Usage Example

```python
from mahjong.meld import Meld
from mahjong.tile import TilesConverter

# Create a PON meld
pon_tiles = TilesConverter.string_to_136_array(pin='333')
pon_meld = Meld(meld_type=Meld.PON, tiles=pon_tiles)

# Create a CHI meld
chi_tiles = TilesConverter.string_to_136_array(sou='567')
chi_meld = Meld(meld_type=Meld.CHI, tiles=chi_tiles)

# Create a KAN meld
kan_tiles = TilesConverter.string_to_136_array(man='2222')
kan_meld = Meld(meld_type=Meld.KAN, tiles=kan_tiles, opened=False)  # closed kan
```

## Current Implementation Issue

In the current codebase (`/Users/hiromu.nakamura.001/ghq/github.com/po3rin/llmmj/llmmj/llmmj.py`), the `convert_melds_to_mahjong_format` function on line 62 currently treats all melds as PON:

```python
# 仮の実装: すべての鳴きをポンとして扱う
result.append(Meld(meld_type=Meld.PON, tiles=tiles))
```

This should be updated to properly detect and handle different meld types (CHI, PON, KAN) based on the tiles provided.

## Note

The `CHANKAN` constant that might appear in older code has been deprecated and replaced with `SHOUMINKAN`.