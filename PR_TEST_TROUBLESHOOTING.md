# PRテストのトラブルシューティングガイド

PRテストが通らない問題を解決するためのガイドです。

## 作成したワークフロー

### 1. PR Check (.github/workflows/pr-check.yml)
**目的**: 詳細なデバッグ情報付きの段階的PRチェック

**実行ステップ**:
1. **環境情報表示**: UV、Python、プロジェクト構造の確認
2. **基本依存関係インストール**: pytest、ruffのみ先行インストール
3. **基本Python機能テスト**: unittest.mockの動作確認
4. **全依存関係インストール**: uv sync --dev実行
5. **エンティティimportテスト**: pydantic、entity.entityのインポート確認
6. **基本linting**: ruffによるコードチェック
7. **モック機能テスト**: unittestとmockの動作確認
8. **分離テスト実行**: 外部依存なしのテスト実行
9. **実際のテストファイル試行**: 実際のpytestテスト実行

### 2. PR Check Minimal (.github/workflows/pr-check-minimal.yml)
**目的**: 最小限の構文チェックと基本機能確認

**実行ステップ**:
1. **構文チェック**: 全Pythonファイルのコンパイルチェック
2. **YAMLチェック**: ワークフローファイルの構文確認
3. **依存関係チェック**: UV依存関係インストールテスト
4. **基本importテスト**: 主要モジュールのインポート確認
5. **簡単なテスト**: 最小限のunittestテスト実行

## よくある問題と解決方法

### 1. 依存関係のインストール失敗

**症状**:
```
✗ pydantic import failed: No module named 'pydantic'
✗ entity.entity import failed: No module named 'pydantic'
```

**原因**: 
- `uv sync --dev`が失敗している
- pyproject.tomlの依存関係定義に問題がある
- uvのバージョンが古い

**解決方法**:
```bash
# ローカルで確認
uv --version  # 最新版を確認
uv sync --dev --verbose  # 詳細ログで確認
uv pip list | grep pydantic  # インストール確認
```

### 2. インポートエラー

**症状**:
```
ModuleNotFoundError: No module named 'entity'
```

**原因**:
- PYTHONPATHが設定されていない
- 作業ディレクトリが間違っている

**解決方法**:
- 環境変数でPYTHONPATH=.を設定済み
- pyproject.tomlでpythonpath = ["."]を設定済み

### 3. テストファイルの構文エラー

**症状**:
```
SyntaxError: invalid syntax
```

**解決方法**:
```bash
# ローカルで構文チェック
python -m py_compile tests/test_generator.py
```

### 4. GitHub Actions環境固有の問題

**症状**: ローカルでは動作するがGitHub Actionsで失敗

**デバッグ方法**:
1. **Debug Tests ワークフロー**を手動実行
2. **PR Check**ワークフローのログを詳細確認
3. 環境変数の違いを確認

## ワークフローの使い分け

### 開発中
```bash
# ローカルで事前チェック
make ci-check

# 問題があれば個別確認
PYTHONPATH=. uv run pytest tests/test_generator.py::TestMahjongQuestionGenerator::test_init_simple_mode -v
```

### PR作成時
1. **PR Check (Minimal)**: 高速な基本チェック
2. **PR Check**: 詳細なデバッグ情報付きチェック

### 問題発生時
1. **Debug Tests**: 手動実行で詳細診断
2. ログの段階的確認:
   - 環境情報 → 依存関係インストール → インポート → テスト実行

## デバッグ手順

### Step 1: 基本環境確認
```bash
# GitHub Actionsログで確認
=== Environment Info ===
uv --version
uv run python --version
PYTHONPATH: .
```

### Step 2: 依存関係確認
```bash
# インストールログで確認
=== Installing all dependencies ===
uv sync --dev --verbose
```

### Step 3: インポート確認
```bash
# 段階的インポートテスト
✓ pydantic available
✓ entity.entity import successful
```

### Step 4: テスト実行確認
```bash
# 分離テストから実際のテストへ
✓ Isolated generator test works
✓ Mock functionality works
```

## 緊急対応

PRテストが通らない場合の緊急対応：

1. **PR Check (Minimal)**が通るかチェック
2. 構文エラーがある場合は優先修正
3. 依存関係の問題は`uv.lock`の再生成を検討
4. 環境固有の問題は**Debug Tests**ワークフローで詳細診断

## 連絡先・参考資料

- **LOCAL_DEVELOPMENT.md**: ローカル環境での実行方法
- **GITHUB_ACTIONS_GUIDE.md**: CI/CD全体の説明
- **Makefile**: ローカルでのGitHub Actions相当コマンド

これらのワークフローとガイドにより、PRテストの問題を段階的に特定・解決できます。