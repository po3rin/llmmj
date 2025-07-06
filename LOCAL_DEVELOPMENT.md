# ローカル開発環境ガイド

このガイドでは、ローカル環境でGitHub Actionsと同じ結果を得るための設定と実行方法を説明します。

## 環境の統一

### 1. 前提条件

- **Python 3.12** をインストール
- **UV** をインストール (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. 環境設定

```bash
# 1. 環境変数ファイルを作成
cp .env.example .env

# 2. 依存関係をインストール
uv sync --dev

# 3. GitHub Actionsと同じ環境をセットアップ
make ci-setup
```

## 実行コマンド

### GitHub Actionsと同じチェックを実行

```bash
# 全てのチェックを実行（推奨）
make ci-check

# または個別に実行
make check          # linting (GitHub Actionsと同じ)
make test           # pytest (GitHub Actionsと同じ)
make test-generator # generator tests のみ
make test-evaluator # evaluator tests のみ
make test-all       # 全てのテスト
```

### 開発中の便利コマンド

```bash
# コードフォーマット
make format

# linting のみ
make lint

# 環境クリーンアップ
make clean
```

## ローカルとGitHub Actionsの違いの原因と対策

### 1. 環境変数の違い

**問題**: `PYTHONPATH` が設定されていない
**対策**: 
```bash
# .envファイルに設定済み
PYTHONPATH=.

# またはMakefileで自動設定
make ci-check  # PYTHONPATH=. が自動で設定される
```

### 2. UVバージョンの違い

**問題**: ローカルとCI環境でUVバージョンが異なる
**対策**:
```bash
# UVを最新バージョンに更新
curl -LsSf https://astral.sh/uv/install.sh | sh

# バージョン確認
uv --version
```

### 3. Python バージョンの違い

**問題**: ローカルのPythonバージョンがGitHub Actions (3.12) と異なる
**対策**:
```bash
# Python 3.12 をインストール（UVで管理）
uv python install 3.12

# プロジェクトでPython 3.12を使用
uv python pin 3.12
```

### 4. キャッシュディレクトリの違い

**問題**: キャッシュの場所が異なり、結果が変わる
**対策**: `.env` ファイルで統一
```bash
UV_CACHE_DIR=./.uv-cache
RUFF_CACHE_DIR=./.ruff-cache
PYTEST_CACHE_DIR=./.pytest_cache
```

### 5. 作業ディレクトリの違い

**問題**: 相対パスの解釈が異なる
**対策**: 
```bash
# プロジェクトルートで実行
cd /path/to/project

# PYTHONPATHを明示的に設定
export PYTHONPATH=.

# または Makefileを使用（自動設定）
make ci-check
```

## トラブルシューティング

### import エラーが発生する場合

```bash
# 1. PYTHONPATH が設定されているか確認
echo $PYTHONPATH

# 2. 手動でPYTHONPATHを設定
export PYTHONPATH=.

# 3. Makefileを使用（推奨）
make ci-check
```

### Ruff の結果が異なる場合

```bash
# 1. Ruff設定を確認
uv run ruff config

# 2. キャッシュをクリア
make clean

# 3. GitHub Actionsと同じ形式で実行
PYTHONPATH=. uv run ruff check . --output-format=github
```

### pytest の結果が異なる場合

```bash
# 1. pytest設定を確認
uv run pytest --help

# 2. GitHub Actionsと同じオプションで実行
PYTHONPATH=. uv run pytest -v

# 3. pyproject.toml の設定を確認
# [tool.pytest.ini_options] セクションをチェック
```

## 推奨ワークフロー

### 開発中

```bash
# 1. コード変更後
make format        # コードをフォーマット

# 2. コミット前
make ci-check      # GitHub Actionsと同じチェック

# 3. プッシュ前
make test-all      # 全てのテスト実行
```

### デバッグ時

```bash
# 1. 環境情報を確認
uv --version
uv run python --version
echo $PYTHONPATH

# 2. インポートテスト
PYTHONPATH=. uv run python -c "import entity.entity; print('OK')"

# 3. 個別テスト実行
PYTHONPATH=. uv run pytest tests/test_generator.py::TestMahjongQuestionGenerator::test_init_simple_mode -v
```

## GitHub Actions との完全一致確認

```bash
# 以下のコマンドの結果がGitHub Actionsと一致することを確認
make ci-check

# 個別確認
PYTHONPATH=. uv run ruff check . --output-format=github
PYTHONPATH=. uv run ruff format --check .
PYTHONPATH=. uv run pytest -v
```

この設定により、ローカル環境でもGitHub Actionsと同じ結果を得ることができます。