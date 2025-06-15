# Mahjong Calculation Protocol (MCP) Server

麻雀の点数計算を行うためのAPIサーバーです。

## 機能

- 手牌から点数計算
- 役判定
- 符数計算
- 飜数計算

## 使用方法

### サーバーの起動

```bash
python mcp_server.py
```

### APIエンドポイント

#### 点数計算

```http
POST /calculate
Content-Type: application/json

{
    "hand": {
        "tiles": ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "1p", "2p", "3p", "4p"],
        "dora_indicators": ["5m"],
        "is_riichi": true,
        "is_tsumo": true
    },
    "melds": [],
    "round_wind": "east",
    "player_wind": "east"
}
```

レスポンス:

```json
{
    "han": 3,
    "fu": 40,
    "score": 5200,
    "yaku": [
        {"name": "リーチ", "han": 1},
        {"name": "一発", "han": 1},
        {"name": "ドラ", "han": 1}
    ]
}
```

#### ヘルスチェック

```http
GET /health
```

レスポンス:

```json
{
    "status": "ok"
}
```

## 牌の表記

- 数牌: `1m` (一萬), `2m` (二萬), ..., `9m` (九萬)
- 筒子: `1p` (一筒), `2p` (二筒), ..., `9p` (九筒)
- 索子: `1s` (一索), `2s` (二索), ..., `9s` (九索)
- 字牌: `1z` (東), `2z` (南), `3z` (西), `4z` (北), `5z` (白), `6z` (發), `7z` (中)

## 開発

### 依存関係

- FastAPI
- uvicorn
- majang (TODO: 実装)

### セットアップ

```bash
pip install -r requirements.txt
```

### テスト

```bash
pytest
``` 