## Vertex AIでvLLMとLoRA/QLoRAを用いたLLMのファインチューニングを行うチュートリアル

このチュートリアルでは、Google CloudのVertex AIを使用して、vLLMとLoRA (Low-Rank Adaptation) またはQLoRA (Quantized LoRA) を活用し、大規模言語モデル (LLM) をファインチューニングする手順を詳細に説明します。

### はじめに

**vLLM** は、Transformerモデルの推論を高速化するライブラリであり、ファインチューニング後の推論フェーズで特にその恩恵を受けます。**LoRA** および **QLoRA** は、LLM全体をファインチューニングする代わりに、少数のアダプター層のみを学習することで、効率的にモデルを特定のタスクに適応させるための手法です。これにより、計算リソースとストレージ要件を大幅に削減できます。

**Vertex AI** は、機械学習モデルの構築、デプロイ、管理を行うための統合プラットフォームです。このチュートリアルでは、Vertex AIのカスタムトレーニング機能を使用して、これらの技術を組み合わせます。

### ターゲット読者

  * LLMのファインチューニングに興味があるデータサイエンティスト、機械学習エンジニア
  * 計算リソースを効率的に使用したい方
  * Vertex AIの利用経験がある、または学習意欲のある方

### 前提条件

  * Google Cloud Platform (GCP) アカウントとプロジェクト
  * GCPプロジェクトでVertex AI APIが有効になっていること
  * `gcloud` CLIが設定済みであること
  * Pythonの基礎知識
  * Gitの基礎知識

### チュートリアル構成

1.  **環境構築と準備**
      * GCPプロジェクトの選択とAPIの有効化
      * 必要な権限の設定
      * Vertex AI SDK for Pythonのインストール
2.  **データセットの準備**
      * ファインチューニング用データセットの準備 (例: SQuAD, Alpacaデータセット形式など)
      * Cloud Storageへのアップロード
3.  **トレーニングスクリプトの作成**
      * ベースモデルの選択 (例: Llama 3, Mistral, Gemmaなど)
      * LoRA/QLoRAの設定
      * vLLMの利用 (推論時に効果を発揮するため、トレーニングスクリプト内では直接的にvLLMの推論エンジンを呼び出すわけではありませんが、推論時にvLLMを使用することを前提としたモデルの保存を行います)
      * Hugging Face `transformers` と `peft` ライブラリの使用
      * Vertex AIカスタムトレーニング用に調整
4.  **Vertex AIカスタムトレーニングの実行**
      * カスタムコンテナイメージのビルド (必要に応じて)
      * トレーニングジョブの定義と実行
      * ログとメトリクスの監視
5.  **ファインチューニングされたモデルのデプロイと推論**
      * Cloud Storageへのモデルの保存
      * Vertex AIエンドポイントへのデプロイ
      * vLLMを使用した推論 (カスタムコンテナでのvLLM利用)
      * 推論の実行と検証

-----

### 1\. 環境構築と準備

#### 1.1 GCPプロジェクトの選択とAPIの有効化

1.  Google Cloud Consoleにログインします。
2.  既存のプロジェクトを選択するか、新しいプロジェクトを作成します。
3.  以下のAPIを有効にします（ナビゲーションメニュー -\> APIとサービス -\> 有効なAPIとサービス）。
      * **Vertex AI API**
      * **Cloud Storage API**
      * **Container Registry API** (または **Artifact Registry API**)

#### 1.2 必要な権限の設定

Vertex AIカスタムトレーニングジョブを実行するための適切な権限が必要です。通常、以下のロールを持つサービスアカウントまたはユーザーを使用します。

  * `Vertex AI User`
  * `Storage Object Admin` (データセットとモデルの保存のため)
  * `Service Account User` (カスタムトレーニングジョブが使用するサービスアカウントとして動作するため)

Google Cloud ConsoleのIAM管理ページで確認・設定してください。

#### 1.3 Vertex AI SDK for Pythonのインストール

ローカル環境でVertex AI SDKを使用するためにインストールします。

```bash
pip install google-cloud-aiplatform google-cloud-storage
```

-----

### 2\. データセットの準備

ファインチューニングには、タスクに適したデータセットが必要です。ここでは、簡潔にするために一般的な指示追従 (instruction tuning) フォーマットを例にします。

**データ形式の例 (JSONL):**

```jsonl
{"instruction": "What is the capital of France?", "output": "Paris"}
{"instruction": "Write a short poem about a cat.", "output": "A furry friend, a gentle purr,\nLies in a sunbeam, soft as fur.\nA graceful leap, a playful chase,\nBringing joy to every space."}
```

#### 2.1 データセットの作成

小さなテストデータセットを`dataset.jsonl`として作成します。

```python
# generate_dataset.py
import json

data = [
    {"instruction": "What is the capital of Japan?", "output": "Tokyo"},
    {"instruction": "List three common fruits.", "output": "Apple, Banana, Orange"},
    {"instruction": "Explain the concept of 'machine learning' in one sentence.", "output": "Machine learning is a field of artificial intelligence that enables systems to learn from data without explicit programming."},
    {"instruction": "Write a short story about a brave knight.", "output": "Sir Reginald, a knight of unwavering courage, embarked on a perilous quest to rescue the kidnapped princess. Through treacherous forests and over towering mountains, he faced mythical beasts and cunning sorcerers, his resolve never faltering. Finally, he confronted the dragon holding the princess captive, and with a mighty blow, vanquished the beast, returning the princess safely to her kingdom, hailed as a true hero."}
]

with open("dataset.jsonl", "w", encoding="utf-8") as f:
    for entry in data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("dataset.jsonl created.")
```

#### 2.2 Cloud Storageへのアップロード

データセットをCloud Storageバケットにアップロードします。

```bash
# バケット名を環境に合わせて変更してください
export GCS_BUCKET="gs://your-vertex-ai-bucket"
gsutil cp dataset.jsonl $GCS_BUCKET/data/
```

-----

### 3\. トレーニングスクリプトの作成

ここでは、`transformers` と `peft` ライブラリを使用して、LoRA (またはQLoRA) ファインチューニングを行うPythonスクリプトを作成します。このスクリプトは、Vertex AIのカスタムトレーニングジョブから実行されることを想定しています。

**`train.py`**

```python
import argparse
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset

def main(args):
    # Quantization Config (for QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=False,
    )

    # Load Model and Tokenizer
    model_name = args.model_name
    print(f"Loading model: {model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config, # Apply quantization for QLoRA
        device_map="auto",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2" if args.use_flash_attention else "eager",
    )
    model.config.use_cache = False # Disable cache for LoRA training
    model = prepare_model_for_kbit_training(model) # Prepare model for QLoRA

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right" # Important for causal LMs

    # LoRA Config
    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=args.lora_target_modules.split(',') if args.lora_target_modules else None,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Load Dataset
    print(f"Loading dataset from: {args.data_path}")
    # dataset = load_dataset("json", data_files=args.data_path, split="train") # for local file
    # For GCS, you might need to download it first or use fsspec
    # For simplicity, assuming data_path is a local path within the container
    # For GCS: you'd typically copy it to /tmp/data/ in your Dockerfile or entrypoint
    # Or use datasets library's fsspec integration if configured correctly (requires GCS credentials in container)
    # A simpler approach for Vertex AI is to pass GCS path and copy it down in the training script
    
    # --- Example for copying from GCS within the script ---
    if args.data_path.startswith("gs://"):
        print(f"Downloading data from GCS: {args.data_path}")
        local_data_path = "/tmp/dataset.jsonl"
        os.makedirs(os.path.dirname(local_data_path), exist_ok=True)
        import subprocess
        subprocess.run(["gsutil", "cp", args.data_path, local_data_path], check=True)
        dataset = load_dataset("json", data_files=local_data_path, split="train")
    else:
        dataset = load_dataset("json", data_files=args.data_path, split="train")
    # ----------------------------------------------------


    def tokenize_function(examples):
        full_text = []
        for instruction, output in zip(examples["instruction"], examples["output"]):
            # Format according to Alpaca/Instruction Tuning format
            # Adjust this prompt template based on your base model's training
            prompt = f"### Instruction:\n{instruction}\n\n### Output:\n{output}"
            full_text.append(prompt)
        return tokenizer(full_text, truncation=True, max_length=args.max_seq_length)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Training Arguments
    training_arguments = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        optim="paged_adamw_8bit", # Recommended for QLoRA
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        fp16=False, # Use bfloat16 for better precision with QLoRA
        bf16=True,
        max_grad_norm=0.3,
        max_steps=-1, # Or specify a number of steps
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="cosine",
        report_to="none", # Vertex AI handles logging separately
    )

    # Trainer
    from trl import SFTTrainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=tokenized_dataset,
        peft_config=peft_config,
        dataset_text_field="output", # This is just a placeholder if not using SFTTrainer's formatting. Actual formatting is in tokenize_function.
        max_seq_length=args.max_seq_length,
        tokenizer=tokenizer,
        args=training_arguments,
    )

    # Train
    print("Starting training...")
    trainer.train()

    # Save trained model (LoRA adapters)
    print(f"Saving model to {args.output_dir}")
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    # Optional: Merge LoRA adapters into base model for full model saving (useful for vLLM deployment)
    # This might require more memory. If you're memory constrained, deploy adapters separately
    # and merge on the serving side, or use vLLM's peft support directly if available.
    # For simplicity, we'll save adapters and assume vLLM can load them or merge happens later.
    # If you want to merge and save a full model:
    try:
        merged_model = model.merge_and_unload()
        merged_model_path = os.path.join(args.output_dir, "merged_model")
        print(f"Saving merged model to {merged_model_path}")
        merged_model.save_pretrained(merged_model_path)
        tokenizer.save_pretrained(merged_model_path)
    except Exception as e:
        print(f"Could not merge model (likely out of memory): {e}. Saving adapters only.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, default="meta-llama/Llama-2-7b-hf") # Example model
    parser.add_argument("--data_path", type=str, required=True, help="Path to the training data (JSONL). Can be GCS path.")
    parser.add_argument("--output_dir", type=str, default="/gcs/your-vertex-ai-bucket/model", help="GCS path for saving the model.")
    parser.add_argument("--num_train_epochs", type=int, default=1)
    parser.add_argument("--per_device_train_batch_size", type=int, default=4)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--weight_decay", type=float, default=0.001)
    parser.add_argument("--max_seq_length", type=int, default=512)
    parser.add_argument("--lora_r", type=int, default=16)
    parser.add_argument("--lora_alpha", type=int, default=32)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    parser.add_argument("--lora_target_modules", type=str, default="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj", help="Comma-separated list of target modules for LoRA.")
    parser.add_argument("--save_steps", type=int, default=500)
    parser.add_argument("--logging_steps", type=int, default=50)
    parser.add_argument("--use_flash_attention", action="store_true", help="Use Flash Attention 2 if available.")

    args = parser.parse_args()
    main(args)
```

**重要なポイント:**

  * **`BitsAndBytesConfig`**: QLoRAを使用するために4ビット量子化を設定します。
  * **`prepare_model_for_kbit_training`**: 量子化されたモデルをPEFTトレーニング用に準備します。
  * **`LoraConfig`**: LoRAアダプターのハイパーパラメータを設定します。`target_modules`は使用するモデルによって調整が必要です。一般的には、Attention層のクエリ (`q_proj`)、キー (`k_proj`)、バリュー (`v_proj`)、出力 (`o_proj`) やMLP層 (`gate_proj`, `up_proj`, `down_proj`) などが対象になります。
  * **`SFTTrainer`**: `trl`ライブラリの`SFTTrainer`は、指示チューニングのようなタスクに便利です。`dataset_text_field`は`tokenize_function`内でテキストを結合しているので、ここではあまり影響しませんが、SFTTrainerの機能を使用する場合は適切に設定します。
  * **`output_dir`**: モデルの保存先はGCSパスにする必要があります。Vertex AIは、このGCSパスにトレーニングアーティファクトをアップロードします。
  * **GCSデータの扱い**: トレーニングスクリプト内でGCSパスのデータを直接`load_dataset`で読み込むのは難しい場合があります。最も簡単な方法は、カスタムコンテナの起動スクリプトでGCSから`gsutil cp`でデータを`/tmp`などにコピーし、そこから読み込む方法です。上記のコード例では、トレーニングスクリプト内で`gsutil cp`を呼び出す方法を示しています。

-----

### 4\. Vertex AIカスタムトレーニングの実行

トレーニングスクリプトを実行するために、カスタムコンテナイメージを作成し、Vertex AIカスタムトレーニングジョブを定義します。

#### 4.1 カスタムコンテナイメージのビルド

`Dockerfile`を作成し、トレーニングに必要なライブラリをインストールします。

**`Dockerfile`**

```dockerfile
# Use a base image with Python and CUDA. Adjust as needed for your GPU.
# For Llama 3, typically needs CUDA 12.1+
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set Python alias
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Google Cloud SDK for gsutil
RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=/usr/local/gcloud
ENV PATH="/usr/local/gcloud/bin:${PATH}"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your training script
COPY train.py .

# Command to run the training script. This will be overridden by Vertex AI.
# ENTRYPOINT ["python", "train.py"]
```

**`requirements.txt`**

```
torch==2.3.0  # Or the latest stable version compatible with your CUDA
transformers==4.42.0
peft==0.11.1
accelerate==0.31.0
bitsandbytes==0.43.1
trl==0.9.0
datasets==2.20.0
sentencepiece
protobuf
fsspec[gcs] # For potentially reading directly from GCS with datasets library
```

**コンテナイメージのビルドとプッシュ:**

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-northeast1" # Choose your preferred region, e.g., us-central1, europe-west4

# Build and push to Artifact Registry (recommended over Container Registry)
# Ensure Artifact Registry is enabled: gcloud services enable artifactregistry.googleapis.com
# Create a repository if it doesn't exist:
# gcloud artifacts repositories create llm-finetuning-repo --repository-format=docker --location=$REGION --description="Docker repository for LLM finetuning"

export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/llm-finetuning-repo/vllm-lora-finetune:latest"

docker build -t $IMAGE_URI .
docker push $IMAGE_URI
```

#### 4.2 トレーニングジョブの定義と実行

Vertex AI SDK for Pythonを使用してカスタムトレーニングジョブを定義します。

```python
import google.cloud.aiplatform as aiplatform
import os

# --- Configuration Variables ---
PROJECT_ID = "your-gcp-project-id"
REGION = "asia-northeast1" # Must match where your GCS bucket and Artifact Registry are
GCS_BUCKET_URI = "gs://your-vertex-ai-bucket" # Where your data is and model will be saved
TRAIN_DATA_GCS_PATH = os.path.join(GCS_BUCKET_URI, "data", "dataset.jsonl")
MODEL_OUTPUT_GCS_PATH = os.path.join(GCS_BUCKET_URI, "model", "finetuned_lora_model")
IMAGE_URI = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/llm-finetuning-repo/vllm-lora-finetune:latest"
JOB_NAME = "vllm-lora-finetune-job"

# Machine type for training (e.g., A100 GPUs)
# Refer to Vertex AI pricing and available machine types for your region
# https://cloud.google.com/vertex-ai/docs/training/configure-compute
MACHINE_TYPE = "a2-highgpu-1g" # 1x NVIDIA A100 (40GB)
ACCELERATOR_TYPE = "NVIDIA_TESLA_A100"
ACCELERATOR_COUNT = 1

# --- Initialize Vertex AI SDK ---
aiplatform.init(project=PROJECT_ID, location=REGION)

# --- Define custom job ---
job = aiplatform.CustomContainerTrainingJob(
    display_name=JOB_NAME,
    container_uri=IMAGE_URI,
    model_serving_container_image_uri=None, # Not serving yet, just training
)

# --- Run the training job ---
# Command to execute within the container.
# The args will be passed to your train.py script.
# Ensure that your train.py parses these arguments correctly.
job.run(
    args=[
        f"--model_name=meta-llama/Llama-2-7b-hf", # Adjust base model as needed (e.g., mistralai/Mistral-7B-v0.1)
        f"--data_path={TRAIN_DATA_GCS_PATH}",
        f"--output_dir={MODEL_OUTPUT_GCS_PATH}",
        f"--num_train_epochs=1",
        f"--per_device_train_batch_size=4",
        f"--gradient_accumulation_steps=1",
        f"--learning_rate=2e-4",
        f"--max_seq_length=512",
        f"--lora_r=16",
        f"--lora_alpha=32",
        f"--lora_dropout=0.05",
        f"--lora_target_modules=q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj", # Adjust based on model architecture
        f"--use_flash_attention", # Enable if your GPU and PyTorch version support it
    ],
    replica_count=1,
    machine_type=MACHINE_TYPE,
    accelerator_type=ACCELERATOR_TYPE,
    accelerator_count=ACCELERATOR_COUNT,
    # You can specify a service account if needed for specific permissions (e.g., accessing private models)
    # service_account="your-custom-service-account@your-gcp-project-id.iam.gserviceaccount.com",
    sync=False, # Run asynchronously. Change to True to wait for completion.
)

print(f"Training job started: {job.resource_name}")
print(f"Check logs here: {job.console_url}")
```

**重要なポイント:**

  * **`MODEL_OUTPUT_GCS_PATH`**: トレーニングスクリプトがLoRAアダプターを保存するGCSのパスです。
  * **`MACHINE_TYPE`, `ACCELERATOR_TYPE`, `ACCELERATOR_COUNT`**: 適切なGPUとマシンタイプを選択してください。LLMのファインチューニングには十分なGPUメモリが推奨されます。Llama 2 7BのようなモデルのQLoRAには、通常1つのA100 (40GB) で十分ですが、モデルサイズやバッチサイズによって調整が必要です。
  * **`args`**: `train.py`スクリプトに渡す引数を設定します。`model_name`はHugging Face HubのモデルIDを指定します。
  * **`sync=False`**: ジョブをバックグラウンドで実行し、ローカルスクリプトの実行を続行します。`True`に設定すると、ジョブが完了するまでブロックされます。
  * **ログとメトリクスの監視**: `job.console_url`からCloud LoggingのログとVertex AIのカスタムトレーニングダッシュボードで進捗を監視できます。

-----

### 5\. ファインチューニングされたモデルのデプロイと推論

ファインチューニングされたLoRAアダプターは、ベースモデルと組み合わせて推論に使用できます。vLLMを推論エンジンとして使用することで、高いスループットと低レイテンシを実現できます。

#### 5.1 Cloud Storageへのモデルの保存

`train.py`スクリプトが、`MODEL_OUTPUT_GCS_PATH`にLoRAアダプターを保存します。このチュートリアルでは、adaptersとtokenizerがこのパスに保存されることを前提とします。もし`merged_model`も保存するようにした場合は、そちらのパスを使用します。

#### 5.2 vLLMを使用した推論用カスタムコンテナの作成

vLLMは、PEFTアダプターのロードをサポートしています。推論時には、ベースモデルとファインチューニングされたLoRAアダプターをロードします。

**`serve.py`** (vLLMを使った推論サーバー)

```python
import os
import argparse
from fastapi import FastAPI, Request
from vllm import LLM, SamplingParams
import torch
import uvicorn
from transformers import AutoTokenizer

app = FastAPI()

llm = None
tokenizer = None
BASE_MODEL_NAME = None

@app.on_event("startup")
async def startup_event():
    global llm, tokenizer, BASE_MODEL_NAME

    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model_name", type=str, required=True, help="Base Hugging Face model name")
    parser.add_argument("--lora_adapter_path", type=str, default=None, help="GCS or local path to LoRA adapters")
    parser.add_argument("--max_model_len", type=int, default=2048, help="Maximum sequence length for the model")
    parser.add_argument("--quantization", type=str, default=None, help="Quantization method (e.g., 'awq', 'gptq', 'squeezellm', 'eetq', 'fp8')")
    parser.add_argument("--dtype", type=str, default="auto", help="Data type for the model (e.g., 'float16', 'bfloat16', 'auto')")
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9, help="Fraction of GPU memory to use")
    
    args = parser.parse_args()

    BASE_MODEL_NAME = args.base_model_name
    
    # Download LoRA adapters if from GCS
    local_lora_path = None
    if args.lora_adapter_path and args.lora_adapter_path.startswith("gs://"):
        print(f"Downloading LoRA adapters from GCS: {args.lora_adapter_path}")
        local_lora_path = "/tmp/lora_adapters"
        os.makedirs(local_lora_path, exist_ok=True)
        import subprocess
        subprocess.run(["gsutil", "-m", "cp", "-r", f"{args.lora_adapter_path}/*", local_lora_path], check=True)
    elif args.lora_adapter_path:
        local_lora_path = args.lora_adapter_path

    print(f"Loading base model: {BASE_MODEL_NAME}")
    print(f"Loading LoRA adapters from: {local_lora_path}")

    # Initialize vLLM LLM
    llm = LLM(
        model=BASE_MODEL_NAME,
        tokenizer=BASE_MODEL_NAME, # Use base model tokenizer
        max_model_len=args.max_model_len,
        quantization=args.quantization,
        dtype=args.dtype,
        gpu_memory_utilization=args.gpu_memory_utilization,
        # For LoRA, vLLM supports it directly by passing the adapter path
        # As of recent vLLM versions, `lora_adapter_path` argument is typically how you pass it.
        # If your vLLM version is older or doesn't have this, you might need to merge first.
        # Check vLLM documentation for exact PEFT/LoRA loading specifics.
        # Current method:
        enable_lora=True, # Enable LoRA functionality
        lora_adapter_path=local_lora_path, # Path to the LoRA adapter directory
    )
    
    # Load tokenizer separately for prompt formatting if needed
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token # Ensure padding token is set for generation

    print("vLLM and Tokenizer loaded successfully!")

@app.post("/predict")
async def predict(request: Request):
    request_json = await request.json()
    prompt = request_json.get("prompt")
    max_new_tokens = request_json.get("max_new_tokens", 256)
    temperature = request_json.get("temperature", 0.7)
    top_p = request_json.get("top_p", 0.95)
    
    if not prompt:
        return {"error": "No prompt provided"}

    # Format the prompt using the same template as training
    # This is crucial for consistent performance
    formatted_prompt = f"### Instruction:\n{prompt}\n\n### Output:\n"

    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_new_tokens=max_new_tokens,
        stop=["### Instruction:", "### Output:"], # Add stop sequences if your model learns them
    )

    try:
        # For vLLM, pass the formatted prompt
        outputs = llm.generate([formatted_prompt], sampling_params)
        
        generated_text = outputs[0].outputs[0].text
        
        # Post-processing: remove the prompt and any accidental repetitions of the prompt format
        if generated_text.startswith(formatted_prompt):
            generated_text = generated_text[len(formatted_prompt):].strip()

        return {"generated_text": generated_text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # For local testing, you can pass arguments like this:
    # python serve.py --base_model_name meta-llama/Llama-2-7b-hf --lora_adapter_path /path/to/your/local/lora_adapters
    # When deployed on Vertex AI, arguments are passed via container args.
    
    # This block is mainly for uvicorn to run the app.
    # Vertex AI Custom Prediction will handle the entrypoint,
    # and we'll pass the arguments in the deployment.
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model_name", type=str, required=True, help="Base Hugging Face model name")
    parser.add_argument("--lora_adapter_path", type=str, default=None, help="GCS or local path to LoRA adapters")
    parser.add_argument("--max_model_len", type=int, default=2048, help="Maximum sequence length for the model")
    parser.add_argument("--quantization", type=str, default=None, help="Quantization method (e.g., 'awq', 'gptq', 'squeezellm', 'eetq', 'fp8')")
    parser.add_argument("--dtype", type=str, default="auto", help="Data type for the model (e.g., 'float16', 'bfloat16', 'auto')")
    parser.add_argument("--gpu_memory_utilization", type=float, default=0.9, help="Fraction of GPU memory to use")
    
    args = parser.parse_args()
    
    # Store args for startup_event
    import sys
    sys.argv = [sys.argv[0]] # Clear existing sys.argv
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            sys.argv.append(f"--{arg_name}")
            sys.argv.append(str(arg_value))

    # uvicorn runs the app, startup_event will be called
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

**`Dockerfile.serve`** (推論用)

```dockerfile
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Google Cloud SDK for gsutil
RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=/usr/local/gcloud
ENV PATH="/usr/local/gcloud/bin:${PATH}"

# Install vLLM and other dependencies
COPY requirements_serve.txt .
RUN pip install --no-cache-dir -r requirements_serve.txt

# Copy your serving script
COPY serve.py .

# Expose the port for the FastAPI app
EXPOSE 8080

# Command to run the FastAPI app with uvicorn.
# Vertex AI will provide environment variables like AIP_HEALTH_ROUTE and AIP_PREDICT_ROUTE.
# The actual base_model_name and lora_adapter_path will be passed as container args.
ENTRYPOINT ["python", "serve.py"]
```

**`requirements_serve.txt`**

```
vllm==0.4.3 # Use a recent version of vLLM
fastapi==0.111.0
uvicorn==0.30.1
torch==2.3.0 # Or compatible version for vLLM and CUDA
transformers==4.42.0
peft==0.11.1 # If vLLM still needs peft to load LoRA
google-cloud-storage
protobuf
sentencepiece
```

**推論コンテナイメージのビルドとプッシュ:**

```bash
export IMAGE_URI_SERVE="${REGION}-docker.pkg.dev/${PROJECT_ID}/llm-finetuning-repo/vllm-lora-serve:latest"

docker build -f Dockerfile.serve -t $IMAGE_URI_SERVE .
docker push $IMAGE_URI_SERVE
```

#### 5.3 Vertex AIエンドポイントへのデプロイ

```python
import google.cloud.aiplatform as aiplatform
import os

# --- Configuration Variables ---
PROJECT_ID = "your-gcp-project-id"
REGION = "asia-northeast1"
MODEL_DISPLAY_NAME = "vllm-lora-finetuned-model"
ENDPOINT_DISPLAY_NAME = "vllm-lora-finetuned-endpoint"
BASE_MODEL_HF_NAME = "meta-llama/Llama-2-7b-hf" # The base model you finetuned
LORA_ADAPTER_GCS_PATH = os.path.join(GCS_BUCKET_URI, "model", "finetuned_lora_model") # Path where adapters are saved
IMAGE_URI_SERVE = f"{REGION}-docker.pkg.dev/{PROJECT_ID}/llm-finetuning-repo/vllm-lora-serve:latest"

# Machine type for serving (e.g., A100 GPUs)
# Choose based on your model size and desired throughput/latency
SERVING_MACHINE_TYPE = "g2-standard-4" # Example: 1x L4 GPU. Adjust as needed.
SERVING_ACCELERATOR_TYPE = "NVIDIA_L4" # Or "NVIDIA_TESLA_A100" etc.
SERVING_ACCELERATOR_COUNT = 1

# --- Initialize Vertex AI SDK ---
aiplatform.init(project=PROJECT_ID, location=REGION)

# --- Create a Model resource ---
# The model resource points to your serving container and model artifacts.
model = aiplatform.Model.upload(
    display_name=MODEL_DISPLAY_NAME,
    artifact_uri=LORA_ADAPTER_GCS_PATH, # The model artifact path is where your serving container will look for files
                                        # In this case, it's the LoRA adapter path
    serving_container_image_uri=IMAGE_URI_SERVE,
    serving_container_ports=[8080],
    serving_container_predict_route="/predict",
    serving_container_health_route="/health",
    # Pass arguments to your serving container's entrypoint.
    # These will be available as `sys.argv` in your serve.py.
    serving_container_args=[
        f"--base_model_name={BASE_MODEL_HF_NAME}",
        f"--lora_adapter_path={LORA_ADAPTER_GCS_PATH}", # Tell serve.py where to find the adapters
        f"--max_model_len=2048",
        # f"--quantization=awq", # If you want to apply AWQ quantization at serving
        f"--dtype=bfloat16", # Match training dtype for best results, or float16
        f"--gpu_memory_utilization=0.9",
    ],
    # You can also pass environment variables to the serving container
    # serving_container_environment_variables={"HF_HOME": "/tmp/hf_cache"},
    sync=True, # Wait for model upload to complete
)

print(f"Model uploaded: {model.resource_name}")

# --- Deploy the model to an Endpoint ---
endpoint = model.deploy(
    endpoint_id=ENDPOINT_DISPLAY_NAME, # Optional: specify a custom ID
    machine_type=SERVING_MACHINE_TYPE,
    accelerator_type=SERVING_ACCELERATOR_TYPE,
    accelerator_count=SERVING_ACCELERATOR_COUNT,
    min_replica_count=1,
    max_replica_count=1, # Adjust for scaling needs
    sync=True, # Wait for deployment to complete
)

print(f"Endpoint deployed: {endpoint.resource_name}")
print(f"Endpoint URL: {endpoint.public_endpoint_domain_name}")
```

**重要なポイント:**

  * **`artifact_uri`**: `serve.py`スクリプトがLoRAアダプターを見つけるためのパスを指定します。`serve.py`では、このパスから`gsutil cp -r`でローカルにコピーしています。
  * **`serving_container_args`**: 推論コンテナの起動時に`serve.py`に渡される引数です。`base_model_name`と`lora_adapter_path`は必須です。
  * **`machine_type`, `accelerator_type`, `accelerator_count`**: 推論に必要なGPUとマシンタイプを選択します。vLLMはGPUメモリを効率的に利用するため、トレーニングよりも少ないGPUでデプロイできる場合があります。
  * **`min_replica_count`, `max_replica_count`**: エンドポイントの自動スケーリングを設定します。

#### 5.4 推論の実行と検証

デプロイされたエンドポイントに対して予測リクエストを送信します。

```python
import google.cloud.aiplatform as aiplatform
import os

PROJECT_ID = "your-gcp-project-id"
REGION = "asia-northeast1"
ENDPOINT_DISPLAY_NAME = "vllm-lora-finetuned-endpoint"

aiplatform.init(project=PROJECT_ID, location=REGION)

# Retrieve the deployed endpoint
endpoints = aiplatform.Endpoint.list(filter=f'display_name="{ENDPOINT_DISPLAY_NAME}"')
if not endpoints:
    raise ValueError(f"Endpoint '{ENDPOINT_DISPLAY_NAME}' not found.")
endpoint = endpoints[0]

# Prepare the prediction request
instances = [
    {"prompt": "What is the largest animal in the world?"},
    {"prompt": "Describe the process of photosynthesis briefly."},
]

# Send the prediction request
response = endpoint.predict(instances=instances)

# Process the response
print("Predictions:")
for i, prediction in enumerate(response.predictions):
    original_prompt = instances[i]["prompt"]
    generated_text = prediction["generated_text"]
    print(f"--- Prompt {i+1} ---")
    print(f"Prompt: {original_prompt}")
    print(f"Generated Text:\n{generated_text}\n")

```

-----

### まとめと次のステップ

このチュートリアルでは、Vertex AI上でvLLMとLoRA/QLoRAを使用してLLMをファインチューニングし、デプロイする一連のプロセスを説明しました。

**重要な学習ポイント:**

  * **LoRA/QLoRA**: 効率的なファインチューニングのためのパラメータ効率的な手法。
  * **vLLM**: 高速なLLM推論のためのライブラリ。
  * **Vertex AIカスタムトレーニング**: 任意のPythonスクリプトとコンテナを実行できる柔軟性。
  * **Vertex AIモデルデプロイ**: 高可用性とスケーラビリティを備えたモデルサービング。

**次のステップ:**

  * **より大規模なデータセットでの実験**: 実際のユースケースに合わせてデータセットを準備し、ファインチューニングを行います。
  * **ハイパーパラメータチューニング**: LoRAの`r`、`alpha`、学習率、バッチサイズなどを調整して、モデルの性能を最適化します。Vertex AIのハイパーパラメータチューニング機能を利用することも検討してください。
  * **異なるベースモデルでの実験**: Llama 3、Mistral、Gemmaなど、様々なベースモデルでLoRAファインチューニングを試します。
  * **評価メトリクスの追加**: ファインチューニング後のモデル性能を定量的に評価するためのメトリクス（例: ROUGE, BLEU, F1スコアなど）を導入します。
  * **CI/CDパイプラインの構築**: Vertex AI Pipelinesを使用して、データ準備からトレーニング、デプロイまでのワークフローを自動化します。

このチュートリアルが、Vertex AIでLLMのファインチューニングを開始するための良い出発点となることを願っています。ご不明な点がありましたら、お気軽にご質問ください。