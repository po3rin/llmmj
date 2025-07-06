# Simple Workflows

シンプルなワークフロー構成に変更しました。

## ワークフロー構成

全てのワークフローは以下のシンプルな構成になっています：

1. **uv sync** - 依存関係のインストール
2. **uv run pytest** - テストの実行

## ワークフローファイル

- **`.github/workflows/pr-check.yml`** - PRチェック
- **`.github/workflows/test.yml`** - メインテスト
- **`.github/workflows/nightly.yml`** - 夜間テスト
- **`.github/workflows/debug.yml`** - デバッグ用（手動実行のみ）

## ローカル開発

```bash
# 依存関係のインストール
make install
# または
uv sync

# テスト実行
make test
# または
uv run pytest

# Linting
make lint
# または
uv run ruff check .

# コード整形
make format
# または
uv run ruff format .
```

## 環境変数

全てのワークフローで `PYTHONPATH=.` が設定されています。

## 依存関係

- `pyproject.toml` - 依存関係の定義
- `uv.lock` - 依存関係のロック
- `uv sync` - 依存関係の同期

これで全てがシンプルになりました！