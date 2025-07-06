# PRワークフローの修正内容

PRテストが失敗していた問題を修正しました。

## 主な修正内容

### 1. 依存関係の問題解決

**修正前の問題**:
- `pydantic`が明示的に定義されていない
- 依存関係の解決に失敗していた

**修正内容**:
- `pyproject.toml`に`pydantic>=2.0.0`を明示的に追加

```toml
dependencies = [
    # ... 他の依存関係
    "pydantic>=2.0.0",
    # ... 
]
```

### 2. テストファイルのimport修正

**修正前の問題**:
```python
from exceptions import AgentSetupError, JSONParseError
```

**修正後**:
```python
from exceptions.exceptions import AgentSetupError, JSONParseError
```

**修正したファイル**:
- `tests/test_generator.py`
- `tests/test_evaluator.py`
- `tests/test_agents_evaluator.py`
- `tests/test_evaluator_libs.py`

### 3. ワークフローの段階的改善

**作成したワークフロー**:

1. **`.github/workflows/pr-check-basic.yml`**
   - Python標準機能のみを使用
   - UVに依存しない最小限のテスト

2. **`.github/workflows/pr-check-uv-simple.yml`**
   - UVを使用した最小限のテスト
   - 段階的な問題特定

3. **`.github/workflows/pr-check.yml`** (メイン)
   - 完全な段階的テスト
   - 基本テスト → インポート確認 → 本格テスト

4. **`tests/test_basic.py`**
   - 外部依存なしの基本テスト
   - Mock機能のテスト

### 4. 修正後のワークフロー実行順序

```
1. 基本機能テスト (test_basic.py)
   ↓
2. 依存関係インストール確認
   ↓
3. 重要モジュールのインポート確認
   ↓
4. 構文チェック
   ↓
5. Linting
   ↓
6. 主要テストケース実行
   ↓
7. 全テスト実行
```

## 使用方法

### 開発時の事前チェック

```bash
# 基本的な動作確認
PYTHONPATH=. python -c "
import exceptions.exceptions
import entity.entity
print('✓ All imports successful')
"

# テスト実行
uv run pytest tests/test_basic.py -v
uv run pytest tests/test_generator.py::TestMahjongQuestionGenerator::test_init_simple_mode -v
```

### ワークフローの使い分け

- **PR Check (Basic)**: Python標準機能のみ、最速
- **PR Check (UV Simple)**: UVの基本機能確認
- **PR Check**: 完全なテストスイート

## 今後の対応

1. **依存関係の安定化**
   - 定期的な`uv.lock`の更新
   - 依存関係の互換性確認

2. **テストの改善**
   - より多くの基本テストケース追加
   - 外部依存を最小限に抑えた単体テスト

3. **ワークフローの最適化**
   - 実行時間の短縮
   - 並列実行の活用

## 問題発生時の対応手順

1. **PR Check (Basic)**が失敗する場合
   - 基本的なPython構文エラーをチェック
   - YAML構文を確認

2. **PR Check (UV Simple)**が失敗する場合
   - UVのインストール問題
   - 依存関係の定義問題

3. **PR Check**が失敗する場合
   - 具体的なテストケースの問題
   - インポートエラーの詳細確認

これらの修正により、PRテストが確実に動作するようになりました。