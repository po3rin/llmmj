1. パッケージ管理
   - `uv` のみを使用し、`pip` は絶対に使わない
   - インストール方法：`uv add package`
   - ツールの実行：`uv run tool`
   - アップグレード：`uv add --dev package --upgrade-package package`
   - 禁止事項：`uv pip install`、`@latest` 構文の使用
