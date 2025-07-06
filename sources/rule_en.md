### About Dora Indicator Tiles

A "dora indicator tile" is a tile that **indicates what the dora tile is for that round** in a mahjong game. The dora indicator tile itself is not the dora; rather, **the "next tile" after that tile becomes the dora**.

#### What is Dora?
*   "Dora" is a special tile that **increases the winning points by 1 for each dora tile held** when you win.
*   However, dora itself is not a yaku, so you cannot win just by holding dora tiles.
*   **Important**: You cannot win with dora alone. You must have at least one other yaku (such as riichi, tanyao, yakuhai, etc.) to win. Dora only increases han count when you have other valid yaku.
*   There are also types like "uradora" (underneath dora) and "kandora" (kan dora).

#### How Dora is Determined
The rule that the "next tile" after the dora indicator becomes the dora is as follows:
*   **For number tiles (man, pin, sou)**: If the indicator is "1", then "2" becomes dora; if "2", then "3", and so on, with the number increasing by 1. If the indicator is "9", then "1" becomes dora due to the circular nature of numbers.
*   **For wind tiles (East, South, West, North)**:
    *   If "East" is the indicator, then "South" is dora.
    *   If "South", then "West".
    *   If "West", then "North".
    *   If "North", then "East" becomes dora (the order cycles).
*   **For dragon tiles (White, Green, Red)**:
    *   If "White" is the indicator, then "Green" is dora.
    *   If "Green", then "Red".
    *   If "Red", then "White" becomes dora (the order cycles).
    *   Dora for honor tiles, especially dragon tiles, can be confusing, so care is needed.

### Fu Calculation

Fu calculation involves adding the following 4 elements, then rounding up to the nearest 10 fu to determine the base points.

*   **Base points (standard fu)**:
    *   Usually starts at **20 fu**.
    *   For **pinfu (all simples)**, if it's a ron win, it's always **30 fu**, and if it's a tsumo win, it's always **20 fu**.
    *   For **chiitoitsu (seven pairs)**, it's special and **fixed at 25 fu**.

*   **Fu for winning pattern**:
    *   For **menzen ron (closed ron)**, **10 fu** is added.
    *   For **tsumo win**, **2 fu** is added.
    *   For open ron (after calling), it's **0 fu**.

*   **Fu for mentsu (sets)**:
    *   Shuntsu (sequences) are **0 fu**.
    *   For pon (triplets):
        *   Tiles 2-8 are **2 fu**.
        *   Tiles 1, 9, and honor tiles are **4 fu**.
    *   For anko (closed triplets):
        *   Tiles 2-8 are **4 fu**.
        *   Tiles 1, 9, and honor tiles are **8 fu**.
    *   For minkan (open kan):
        *   Tiles 2-8 are **8 fu**.
        *   Tiles 1, 9, and honor tiles are **16 fu**.
    *   For ankan (closed kan):
        *   Tiles 2-8 are **16 fu**.
        *   Tiles 1, 9, and honor tiles are **32 fu**.

*   **Fu for atama (pair)**:
    *   Pairs of tiles 2-8 are **0 fu**.
    *   Pairs of terminals (1, 9) and non-value wind tiles (winds that are neither round wind nor seat wind) are also **0 fu**.
    *   Pairs of dragon tiles (White, Green, Red) or value wind tiles (round wind or seat wind) are **2 fu**.
    *   Pairs of double wind tiles (when round wind and seat wind are the same) are **4 fu**.
    *   **Important**: Honor tile pairs (dragon/wind tiles) only provide fu points, not yaku. Yakuhai yaku requires triplets or quadruplets of honor tiles, not pairs.

*   **Fu for tenpai (waiting pattern)**:
    *   Kantsu (gap) wait is **2 fu**.
    *   Penchan (edge) wait is **2 fu**.
    *   Atama (single tile) wait is **2 fu**.
    *   Ryanmen (two-sided) wait is **0 fu**.
    *   Shanpon (dual pair) wait is **0 fu**.

*   **Final rounding**:
    *   The total fu calculated above is **rounded up to the nearest 10 fu**. This becomes the final base points (fu).

For example, for a non-dealer's 30 fu 1 han, it would be 1,000 points for ron win, 500 points from dealer and 300 points from non-dealers for tsumo win, with the points determined by this fu count and han count.

### Waiting Patterns

The meaning of each waiting pattern is explained below in bullet points. However, **the specific "meaning" or "form" of these waiting patterns themselves is not directly described in the provided sources**. The sources only contain the "fu" values added for each waiting pattern.

The specific forms and meanings of each waiting pattern shown below are **based on general mahjong knowledge and are not directly obtained from the provided sources**. We recommend verifying them independently.

*   **Kantsu (Gap) Wait**
    *   **Fu**: **2 fu**.
    *   **General meaning**: A form where you wait for a tile between two consecutive number tiles to complete a sequence (shuntsu). Example: Holding "2, 4" and waiting for "3", etc.
*   **Penchan (Edge) Wait**
    *   **Fu**: **2 fu**.
    *   **General meaning**: A form where you wait for the end of number tiles to complete a sequence (holding 1-2 and waiting for 3, or holding 8-9 and waiting for 7). Example: Holding "1, 2" and waiting for "3", or holding "7, 8" and waiting for "9", etc.
*   **Atama (Single Tile) Wait**
    *   **Fu**: **2 fu**.
    *   **General meaning**: A form where all mentsu (sets) are complete and you wait for one tile to complete the atama (pair). In other words, a state where you can win if a specific type of tile comes.
*   **Ryanmen (Two-Sided) Wait**
    *   **Fu**: **0 fu**.
    *   **General meaning**: A form where you wait for either side of two consecutive number tiles to complete a sequence. Example: Holding "3, 4" and waiting for "2" or "5", etc. Since you can win with 2 types of tiles, it's considered a relatively advantageous wait.
*   **Shanpon (Dual Pair) Wait**
    *   **Fu**: **0 fu**.
    *   **General meaning**: A form where you have 2 pairs and wait for a tile to make either pair into a triplet (kotsu). Example: Holding "Red, Red" and "Green, Green" and waiting for either "Red" or "Green", etc.

The order of fu calculation is to add "base points of 20 fu", "points for winning pattern", "points for mentsu", and "points for tenpai pattern", then round up the total to the nearest 10 fu to get the base points. Ryanmen wait and shanpon wait don't add fu, but kantsu, penchan, and atama wait add 2 fu, which is a characteristic feature.

### Mahjong Score Reference Table (Non-Dealer Points)

#### For Ron Win
*   **Chiitoitsu (25 fu)**
    *   1 han: **1,600 points**
    *   2 han: **3,200 points**
    *   3 han: **6,400 points**
    *   4 han: **9,600 points**
*   **Pinfu (20 fu)**
    *   1 han: **1,300 points** (However, there's also a note that pinfu ron win is always 30 fu.)
*   **30 fu**
    *   1 han: **1,000 points**
    *   2 han: **2,000 points**
    *   3 han: **3,900 points**
    *   4 han: **7,700 points**
*   **40 fu**
    *   1 han: **1,300 points**
    *   2 han: **2,600 points**
    *   3 han: **5,200 points**
    *   4 han: **Mangan**
*   **50 fu**
    *   1 han: **1,600 points**
    *   2 han: **3,200 points**
    *   3 han: **6,400 points**
    *   4 han: **Mangan**
*   **60 fu**
    *   1 han: **2,000 points**
    *   2 han: **3,900 points**
    *   3 han: **7,700 points**
    *   4 han: **Mangan**
*   **70 fu**
    *   1 han: **2,300 points**
    *   2 han: **4,500 points**
    *   3 han: **Mangan**
    *   4 han: **Mangan**

#### For Tsumo Win (Payment: Non-Dealer/Dealer)
*   **Pinfu (20 fu)**
    *   1 han: **300/500 points**
*   **Chiitoitsu (25 fu)**
    *   1 han: **400/700 points**
    *   2 han: **800/1600 points**
    *   3 han: **1600/3200 points**
    *   4 han: **Mangan**
*   **30 fu**
    *   1 han: **300/500 points**
    *   2 han: **500/1,000 points**
    *   3 han: **1,000/2,000 points**
    *   4 han: **2,000/3,900 points**
*   **40 fu**
    *   1 han: **400/700 points**
    *   2 han: **700/1,300 points**
    *   3 han: **1,300/2,600 points**
    *   4 han: **Mangan**
*   **50 fu**
    *   1 han: **400/800 points**
    *   2 han: **800/1,600 points**
    *   3 han: **1,600/3,200 points**
    *   4 han: **Mangan**
*   **60 fu**
    *   1 han: **500/1,000 points**
    *   2 han: **1,000/2,000 points**
    *   3 han: **2,000/3,900 points**
    *   4 han: **Mangan**
*   **70 fu**
    *   1 han: **600/1,200 points**
    *   2 han: **1,200/2,300 points**
    *   3 han: **Mangan**
    *   4 han: **Mangan**

#### Points for Mangan and Above (Non-Dealer Points)
*   **Mangan (5-7 han)**: **8,000 points**
*   **Haneman (8-10 han)**: **12,000 points**
*   **Baiman (11-12 han)**: **16,000 points**
*   **Sanbaiman (13+ han)**: **24,000 points**
*   **Yakuman**: **32,000 points**

---

### Mahjong Score Reference Table (Dealer Points)

#### For Ron Win
*   **Chiitoitsu (25 fu)**
    *   1 han: **None**
    *   2 han: **2,400 points**
    *   3 han: **4,800 points**
    *   4 han: **9,600 points**
*   **Pinfu (20 fu)**
    *   1 han: **None**
*   **30 fu**
    *   1 han: **1,500 points**
    *   2 han: **2,900 points**
    *   3 han: **5,800 points**
    *   4 han: **11,600 points**
*   **40 fu**
    *   1 han: **2,000 points**
    *   2 han: **3,900 points**
    *   3 han: **7,700 points**
    *   4 han: **Mangan**
*   **50 fu**
    *   1 han: **2,400 points**
    *   2 han: **4,800 points**
    *   3 han: **9,600 points**
    *   4 han: **Mangan**
*   **60 fu**
    *   1 han: **2,900 points**
    *   2 han: **5,800 points**
    *   3 han: **11,600 points**
    *   4 han: **Mangan**
*   **70 fu**
    *   1 han: **3,400 points**
    *   2 han: **6,800 points**
    *   3 han: **Mangan**
    *   4 han: **Mangan**

#### For Tsumo Win (Payment: All)
*   **Pinfu (20 fu)**
    *   1 han: **None**
*   **Chiitoitsu (25 fu)**
    *   1 han: **600 all**
    *   2 han: **1200 all**
    *   3 han: **2400 all**
    *   4 han: **Mangan**
*   **30 fu**
    *   1 han: **500 all**
    *   2 han: **1,000 all**
    *   3 han: **2,000 all**
    *   4 han: **3,900 all**
*   **40 fu**
    *   1 han: **700 all**
    *   2 han: **1,300 all**
    *   3 han: **2,600 all**
    *   4 han: **Mangan**
*   **50 fu**
    *   1 han: **800 all**
    *   2 han: **1,600 all**
    *   3 han: **3,200 all**
    *   4 han: **Mangan**
*   **60 fu**
    *   1 han: **1,000 all**
    *   2 han: **2,000 all**
    *   3 han: **3,900 all**
    *   4 han: **Mangan**
*   **70 fu**
    *   1 han: **1,200 all**
    *   2 han: **2,300 all**
    *   3 han: **Mangan**
    *   4 han: **Mangan**

#### Points for Mangan and Above (Dealer Points)
*   **Mangan (5-7 han)**: **12,000 points**
*   **Haneman (8-10 han)**: **18,000 points**
*   **Baiman (11-12 han)**: **24,000 points**
*   **Sanbaiman (13+ han)**: **36,000 points**
*   **Yakuman**: **48,000 points**

---
**Additional Notes**
*   In fu calculation, pinfu (all simples) ron win is always 30 fu, and tsumo win is always 20 fu.
*   Chiitoitsu (seven pairs) is special and always fixed at 25 fu.
*   Mangan points apply when han count is 5-7.
*   The order of point calculation starts with "base points of 20 fu", then adds "points for winning pattern", "points for mentsu", and "points for tenpai pattern", then **rounds up to the nearest 10 fu to get the base points**.

### Mahjong Yaku List

*   **Riichi**
    *   **Description**: Declare riichi and place 1000 point sticks in the pot.
    *   **Han**: 1 han when closed, cannot call.
*   **Tsumo**
    *   **Description**: Win with a tile drawn by yourself.
    *   **Han**: 1 han when closed, cannot call.
*   **Yakuhai**
    *   **Description**: Collect 3 tiles of White, Green, Red, or round wind/seat wind.
    *   **Han**: 1 han when closed, 1 han when open.
*   **Tanyao**
    *   **Description**: Make hand using only number tiles 2-8.
    *   **Han**: 1 han when closed, 1 han when open.
*   **Pinfu**
    *   **Description**: Mentsu are number sequences, atama is not yakuhai, win with ryanmen wait.
    *   **Han**: 1 han when closed, cannot call.
*   **Sanshoku Doujun**
    *   **Description**: Make same number sequences in man, pin, and sou.
    *   **Han**: 2 han when closed, 1 han when open.
*   **Ikkitsuukan**
    *   **Description**: Make 123, 456, 789 with same suit.
    *   **Han**: 2 han when closed, 1 han when open.
*   **Honitsu**
    *   **Description**: Make hand using only one suit (man, pin, or sou) and honor tiles.
    *   **Han**: 3 han when closed, 2 han when open.
*   **Chinitsu**
    *   **Description**: Make hand using only one suit (man, pin, or sou).
    *   **Han**: 6 han when closed, 5 han when open.
*   **Chiitoitsu**
    *   **Description**: Collect 7 pairs of the same tiles.
    *   **Han**: 2 han when closed, cannot call.
*   **Toitoi**
    *   **Description**: Make all mentsu as triplets (except atama).
    *   **Han**: 2 han when closed, 2 han when open.
*   **Iipeikou**
    *   **Description**: Make 2 identical sequences of same suit and numbers.
    *   **Han**: 1 han when closed, cannot call.
*   **Ryanpeikou**
    *   **Description**: Make 2 sets of iipeikou.
    *   **Han**: 3 han when closed, cannot call.
*   **Chanta**
    *   **Description**: Make hand using only terminals (1, 9) and honor tiles.
    *   **Han**: 2 han when closed, 1 han when open.
*   **Junchan**
    *   **Description**: Make hand using only terminals (1, 9).
    *   **Han**: 3 han when closed, 2 han when open.
*   **Sanankou**
    *   **Description**: Make 3 closed triplets by your own power.
    *   **Han**: 2 han when closed, 2 han when open.
*   **Shousangen**
    *   **Description**: Use one of White, Green, Red as atama and collect 3 of the other two.
    *   **Han**: 2 han when closed, 2 han when open.
*   **Sanshoku Doukou**
    *   **Description**: Make 3 triplets of same numbers in man, pin, and sou.
    *   **Han**: 2 han when closed, 2 han when open.
*   **Honroutou**
    *   **Description**: Make chiitoitsu or toitoi using only terminals (1, 9) and honor tiles.
    *   **Han**: 2 han when closed, 2 han when open.
*   **Sankantsu**
    *   **Description**: Win after calling kan 3 times.
    *   **Han**: 2 han when closed, 2 han when open.
*   **Kokushi Musou**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, cannot call.
*   **Suuankou**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Daisangen**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Shousuushii**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Daisuushii**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Chuurenpoutou**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, cannot call.
*   **Ryuuiisou**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Chinroutou**
    *   **Description**: [No image description, yaku name only].
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Tenhou**
    *   **Description**: Dealer wins with initial 14 tiles.
    *   **Han**: Yakuman when closed, cannot call.
*   **Chihou**
    *   **Description**: Non-dealer wins on first draw.
    *   **Han**: Yakuman when closed, cannot call.
*   **Suukantsu**
    *   **Description**: Win after calling kan 4 times.
    *   **Han**: Yakuman when closed, yakuman when open.
*   **Ippatsu**
    *   **Description**: Win within 1 turn after declaring riichi.
    *   **Han**: 1 han when closed, cannot call.
*   **Daburu Riichi**
    *   **Description**: Declare riichi on first discard.
    *   **Han**: 2 han when closed, cannot call.
*   **Haitei**
    *   **Description**: Win by tsumo on the last tile.
    *   **Han**: 1 han when closed, 1 han when open.
*   **Houtei**
    *   **Description**: Win by ron on the last tile.
    *   **Han**: 1 han when closed, 1 han when open.
*   **Rinshan Kaihou**
    *   **Description**: Win with tile drawn after calling kan.
    *   **Han**: 1 han when closed, 1 han when open.
*   **Chankan**
    *   **Description**: Win with tile from another player's additional kan.
    *   **Han**: 1 han when closed, 1 han when open.