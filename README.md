
# LLMMJ

LLMMJ is a tool for evaluating the performance of Large Language Models (LLMs) in generating Mahjong scoring problems. It provides a framework to test and compare different LLMs' abilities to calculate Mahjong scores correctly.

## Features

- Evaluate multiple LLMs simultaneously
- Generate Mahjong questions with different difficulty levels
- Calculate and validate Mahjong scores
- Compare model performance using pandas DataFrame
- Support for various LLM providers (OpenAI, Anthropic, Google)

## Installation

```bash
# Clone the repository
git clone https://github.com/po3rin/llmmj.git
cd llmmj
uv sync
```

## Usage

### Basic Example

#### evaluation

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from libs.evals import MultiModelEvaluator
from libs.generator import generate_question_prompt_template

# Initialize models　(requires API key)
models = [
    ChatOpenAI(model="gpt-4-turbo-preview"),
    ChatAnthropic(model="claude-3-opus-20240229")
]

evaluator = MultiModelEvaluator(models, generate_question_prompt_template)

dataset = [
    {
        "query": "答えが2飜30符になる問題を作ってください",
        "answer": {
            "han": 2,
            "fu": 30
        }
    }
    # Add more test cases...
]

results_df = evaluator.evals(dataset)
print(results_df.groupby('model')['correct'].mean())  # Accuracy by model
```

#### mcp

```bash
uv run python main.py
```

add settings (ex: Claude Desktop)

```json
{
  "mcpServers": {
    "majang": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```
