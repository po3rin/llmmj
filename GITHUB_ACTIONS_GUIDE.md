# GitHub Actions ガイド

## 作成したワークフロー

### 1. Tests (test.yml)
**トリガー**: main/develop ブランチへのpush、PR作成
**実行内容**: 
- `uv run pytest` でテスト実行
- Ruffでのlinting
- カバレッジレポート生成
- 個別モジュールテスト

### 2. PR Check (pr-check.yml)
**トリガー**: プルリクエスト作成
**実行内容**:
- 軽量なlinting
- `uv run pytest` での基本テスト
- インポート確認

### 3. Nightly Tests (nightly.yml)
**トリガー**: 毎日午前2時 (UTC)、手動実行
**実行内容**:
- 包括的テスト
- HTMLレポート生成
- 依存関係チェック

### 4. Debug Tests (debug.yml)
**トリガー**: 手動実行、debug-** ブランチ
**実行内容**:
- 問題診断用の詳細デバッグ

## ローカルでのテスト実行

```bash
# 依存関係インストール
uv sync --dev

# 全テスト実行
uv run pytest

# 特定モジュールテスト
uv run python tests/run_tests.py generator
uv run python tests/run_tests.py evaluator

# Linting
uv run ruff check .
uv run ruff format .

# カバレッジ付きテスト
uv run pytest --cov=. --cov-report=html
```

## 問題解決

### よくある問題
1. **Import Error**: `pythonpath = ["."]` が pyproject.toml に設定済み
2. **依存関係エラー**: `uv sync --dev` で解決
3. **Linting失敗**: `uv run ruff check . --fix` で自動修正

### デバッグ方法
1. Debug Tests ワークフローを手動実行
2. ローカルで `uv run pytest -v` でテスト
3. `uv run python -c "import sys; print(sys.path)"` でパス確認

## CI/CDパイプライン
- **プッシュ時**: フルテストスイート実行
- **プルリクエスト**: 軽量チェック
- **定期実行**: 毎日包括テスト

全てのワークフローで `uv run pytest` を使用してテストを実行します。