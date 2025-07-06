# テストファイルの概要

evaluatorとgeneratorディレクトリで不足していたテストファイルを作成しました。

## 作成したテストファイル

### 1. test_generator.py
`MahjongQuestionGenerator`クラスの包括的なテストファイルです。

**テスト内容:**
- 初期化テスト（シンプルモード、ツールモード、カスタムテンプレート）
- 問題生成テスト（成功、エラー処理）
- ReActエージェントセットアップテスト
- モデル名抽出テスト
- 鳴きありの手牌処理テスト

**Mock対象:**
- LLMモデル（`model`パラメータ）
- LangChainのPromptTemplate、チェーン実行
- ReActエージェントの作成と実行

### 2. test_evaluator.py
`MahjongEvaluator`と`MultiModelEvaluator`クラスのテストファイルです。

**テスト内容:**
- 初期化テスト
- 評価実行テスト（成功、各種エラー処理）
- 複数モデル評価テスト
- エラーハンドリングテスト（AgentSetupError、JSONParseError、UnknownError）

**Mock対象:**
- MahjongQuestionGenerator
- 評価処理関数（process_hand_generation、hand_2_result）
- DataFrame変換処理

### 3. test_evaluator_libs.py
`evaluator/libs.py`の各関数のテストファイルです。

**テスト内容:**
- `hand_2_result` - 正答/誤答/エラー処理テスト
- `create_error_result` - エラー結果作成テスト
- `process_hand_generation` - 手牌処理テスト（成功/失敗）
- `result_to_df` - DataFrame変換テスト

**Mock対象:**
- スコア計算関数（calculate_score）
- 手牌検証関数（validate_hand）

### 4. test_agents_evaluator.py
`MahjongMultiAgentsEvaluator`クラスのテストファイルです。

**テスト内容:**
- 初期化テスト（sequential/loopモード）
- 非同期手牌生成テスト
- 非同期評価実行テスト
- 同期ラッパーテスト
- エラーハンドリングテスト

**Mock対象:**
- ランナー取得関数（get_sequential_runner、get_loop_runner）
- 実行関数（run）
- 非同期処理（asyncio.run、ThreadPoolExecutor）

### 5. run_tests.py
テスト実行スクリプトです。

**機能:**
- 全テストの実行
- カテゴリ別テスト実行（generator、evaluator）
- テスト結果の集約と表示

## 使用方法

### 全てのテストを実行
```bash
python tests/run_tests.py
```

### generatorテストのみ実行
```bash
python tests/run_tests.py generator
```

### evaluatorテストのみ実行
```bash
python tests/run_tests.py evaluator
```

### 個別のテストファイルを実行
```bash
python -m pytest tests/test_generator.py -v
python -m pytest tests/test_evaluator.py -v
python -m pytest tests/test_evaluator_libs.py -v
python -m pytest tests/test_agents_evaluator.py -v
```

## テストの特徴

### Mock戦略
- **LLM実行部分**: 全てmockして実際のLLMを呼び出さない
- **外部依存関係**: LangChain、pandas、asyncio等をmock
- **内部関数**: 各モジュール間の依存関係をmock

### エラーハンドリング
- カスタム例外（AgentSetupError、JSONParseError、HandValidationError等）
- 未知のエラー（Exception）
- 非同期処理のエラー

### データ検証
- 正答/誤答の判定
- 手牌データの検証
- DataFrame変換の検証

## 依存関係

テストの実行には以下のパッケージが必要です：
- `unittest` (標準ライブラリ)
- `pandas` (データ処理)
- `asyncio` (非同期処理テスト)

## 注意事項

1. **環境依存**: pandasやその他の外部パッケージがインストールされている必要があります
2. **Mock範囲**: 実際のLLM呼び出しは行わないため、プロンプトの内容や実際のLLMの応答品質はテストされません
3. **非同期テスト**: 一部のテストは非同期処理を含むため、Python 3.7以降が必要です

## 今後の改善点

1. **統合テスト**: 実際のLLMを使用したend-to-endテストの追加
2. **パフォーマンステスト**: 大量データでの性能テスト
3. **カバレッジ測定**: テストカバレッジの測定と改善
4. **CI/CD統合**: GitHub ActionsやJenkinsでの自動テスト実行