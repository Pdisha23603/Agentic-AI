"""
QLoRA-style fine-tuning skeleton.py
-----------------------------------
Production-ready QLoRA (Quantized Low-Rank Adaptation) fine-tuning pipeline
for Causal Language Models (e.g., Mistral-7B, LLaMA-3, Qwen-2.5).

Key Architecture & Optimization Highlights:
1. 4-bit NormalFloat (NF4) Quantization via bitsandbytes to minimize VRAM.
2. Double Quantization (Nested Quantization) for additional memory savings.
3. LoRA adapter injection across all linear projections (Attention + MLP).
4. Gradient checkpointing with use_cache=False to prevent VRAM spikes.
5. Paged 8-bit AdamW optimizer for memory-efficient gradient updates.
6. Auto-detection for CUDA, bfloat16, fp16, and CPU fallback.
7. End-to-end dataset handling, evaluation, saving, and inference testing.

Usage:
    python "QLoRA-style fine-tuning skeleton.py"
    python "QLoRA-style fine-tuning skeleton.py" --model_name "Qwen/Qwen2.5-0.5B" --epochs 3
"""

import argparse
import logging
import os
import sys
from typing import Dict, Any, Optional

import torch
from datasets import load_dataset, DatasetDict
from peft import (
    LoraConfig,
    PeftModel,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# Set up clean logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def get_hardware_config():
    """Detects available hardware and configures precision, quantization, and device placement."""
    cuda_available = torch.cuda.is_available()
    
    if cuda_available:
        device_name = torch.cuda.get_device_name(0)
        bf16_supported = torch.cuda.is_bf16_supported()
        compute_dtype = torch.bfloat16 if bf16_supported else torch.float16
        logger.info(f"CUDA GPU detected: {device_name}")
        logger.info(f"Precision config: compute_dtype={compute_dtype}, bf16_supported={bf16_supported}")
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
        )
        return {
            "use_cuda": True,
            "device_map": "auto",
            "bnb_config": bnb_config,
            "compute_dtype": compute_dtype,
            "bf16": bf16_supported,
            "fp16": not bf16_supported,
            "optim": "paged_adamw_8bit",
        }
    else:
        logger.warning(
            "CUDA is not available. Falling back to CPU mode. "
            "Note: 4-bit quantization requires CUDA; running in standard precision."
        )
        return {
            "use_cuda": False,
            "device_map": None,
            "bnb_config": None,
            "compute_dtype": torch.float32,
            "bf16": False,
            "fp16": False,
            "optim": "adamw_torch",
        }


def format_instruction_prompt(example: Dict[str, Any]) -> str:
    """Formats raw dataset items into a standard instruction-following prompt."""
    if "text" in example and example["text"]:
        return example["text"]
    
    instruction = example.get("instruction", "Answer the customer service query.")
    user_input = example.get("input", "")
    response = example.get("response", "")
    
    if user_input:
        prompt = (
            f"### Instruction:\n{instruction}\n\n"
            f"### Input:\n{user_input}\n\n"
            f"### Response:\n{response}"
        )
    else:
        prompt = (
            f"### Instruction:\n{instruction}\n\n"
            f"### Response:\n{response}"
        )
    return prompt


def load_and_prepare_dataset(
    dataset_path: str,
    tokenizer: AutoTokenizer,
    max_length: int = 512,
    test_size: float = 0.1,
):
    """Loads JSONL dataset, applies prompt formatting, tokenizes, and creates train/val splits."""
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset file not found at '{dataset_path}'")
    
    raw_dataset = load_dataset("json", data_files=dataset_path)["train"]
    logger.info(f"Loaded {len(raw_dataset)} raw records from {dataset_path}")

    def tokenize_fn(batch):
        formatted_texts = [
            format_instruction_prompt({k: batch[k][i] for k in batch})
            for i in range(len(batch[next(iter(batch))]))
        ]
        # Tokenize with proper padding & truncation
        tokenized = tokenizer(
            formatted_texts,
            truncation=True,
            max_length=max_length,
            padding=False,  # Dynamic padding handled by DataCollator
        )
        return tokenized

    # Map tokenization and remove raw text columns to avoid trainer tensor mismatch
    column_names = raw_dataset.column_names
    tokenized_dataset = raw_dataset.map(
        tokenize_fn,
        batched=True,
        remove_columns=column_names,
        desc="Tokenizing dataset",
    )

    if len(tokenized_dataset) > 5 and test_size > 0.0:
        split_dataset = tokenized_dataset.train_test_split(test_size=test_size, seed=42)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]
    else:
        train_dataset = tokenized_dataset
        eval_dataset = None

    logger.info(f"Prepared train samples: {len(train_dataset)}, eval samples: {len(eval_dataset) if eval_dataset else 0}")
    return train_dataset, eval_dataset


def get_target_modules_for_model(model: torch.nn.Module):
    """Identifies suitable linear projection target modules for LoRA adaptation."""
    # Standard transformer linear projection names for LLaMA, Mistral, Qwen, Falcon, etc.
    standard_targets = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    
    # Check if standard modules exist in the loaded model
    model_modules = set()
    for name, _ in model.named_modules():
        model_modules.update(name.split("."))
        
    found_targets = [t for t in standard_targets if t in model_modules]
    
    if found_targets:
        return found_targets
    
    # Fallback for GPT-2 / older architectures
    gpt2_targets = ["c_attn", "c_proj", "c_fc"]
    found_gpt2 = [t for t in gpt2_targets if t in model_modules]
    if found_gpt2:
        return found_gpt2
    
    # Minimal fallback
    return ["q_proj", "v_proj"]


def run_training(
    model_name: str = "mistralai/Mistral-7B-v0.1",
    dataset_path: str = "food_cs_queries.jsonl",
    output_dir: str = "./lora-food-cs-adapter",
    num_train_epochs: int = 3,
    per_device_train_batch_size: int = 1,
    gradient_accumulation_steps: int = 8,
    learning_rate: float = 2e-4,
    max_length: int = 512,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    do_test_inference: bool = True,
):
    """Main QLoRA fine-tuning workflow."""
    logger.info("=" * 60)
    logger.info(f"Starting QLoRA Fine-Tuning Pipeline for model: {model_name}")
    logger.info("=" * 60)

    # 1. Hardware and Quantization Config
    hw_config = get_hardware_config()

    # 2. Tokenizer Setup
    logger.info(f"Loading tokenizer for '{model_name}'...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
    )
    # Ensure padding token is set for causal LM
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "right"  # Required for Causal LM training

    # 3. Load Model
    logger.info(f"Loading base model '{model_name}' with 4-bit quantization config...")
    model_kwargs = {
        "trust_remote_code": True,
    }
    if hw_config["use_cuda"] and hw_config["bnb_config"] is not None:
        model_kwargs["quantization_config"] = hw_config["bnb_config"]
        model_kwargs["device_map"] = hw_config["device_map"]
    else:
        model_kwargs["torch_dtype"] = hw_config["compute_dtype"]

    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    
    # Explicitly configure pad_token_id and disable use_cache for gradient checkpointing
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    # Prepare model for k-bit training if quantized
    if hw_config["use_cuda"] and hw_config["bnb_config"] is not None:
        model = prepare_model_for_kbit_training(
            model,
            use_gradient_checkpointing=True,
        )

    # 4. Configure LoRA PEFT Adapter
    target_modules = get_target_modules_for_model(model)
    logger.info(f"Configuring LoRA on target modules: {target_modules}")

    peft_config = LoraConfig(
        r=lora_r,
        lora_alpha=lora_alpha,
        target_modules=target_modules,
        lora_dropout=lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    
    logger.info("Trainable parameters summary:")
    model.print_trainable_parameters()

    # 5. Load and Tokenize Dataset
    train_dataset, eval_dataset = load_and_prepare_dataset(
        dataset_path=dataset_path,
        tokenizer=tokenizer,
        max_length=max_length,
    )

    # 6. Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=per_device_train_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=num_train_epochs,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        optim=hw_config["optim"],
        fp16=hw_config["fp16"],
        bf16=hw_config["bf16"],
        logging_steps=1,
        save_strategy="epoch",
        evaluation_strategy="epoch" if eval_dataset is not None else "no",
        eval_strategy="epoch" if eval_dataset is not None else "no",
        save_total_limit=2,
        report_to="none",
        remove_unused_columns=True,
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
    )

    # 7. Train Model
    logger.info("Starting training loop...")
    trainer.train()

    # 8. Save Adapter and Tokenizer
    logger.info(f"Saving trained LoRA adapter and tokenizer to '{output_dir}'...")
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("LoRA fine-tuning completed and saved successfully!")

    # 9. Test Inference Demonstration
    if do_test_inference:
        logger.info("=" * 60)
        logger.info("Running Post-Fine-Tuning Inference Test...")
        logger.info("=" * 60)
        run_inference_demo(
            base_model_name=model_name,
            adapter_path=output_dir,
            sample_query="My pizza was delivered completely cold and smashed. Can I get a refund?",
        )


def run_inference_demo(
    base_model_name: str,
    adapter_path: str,
    sample_query: str,
):
    """Loads the base model with fine-tuned LoRA adapters and runs a sample query generation."""
    try:
        logger.info(f"Loading base model '{base_model_name}' for inference...")
        tokenizer = AutoTokenizer.from_pretrained(adapter_path)
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.bfloat16 if (torch.cuda.is_available() and torch.cuda.is_bf16_supported()) else torch.float32
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch_dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )
        
        logger.info(f"Attaching LoRA adapter from '{adapter_path}'...")
        peft_model = PeftModel.from_pretrained(base_model, adapter_path)
        peft_model.eval()

        prompt = (
            f"### Instruction:\nHandle customer query regarding cold or damaged food.\n\n"
            f"### Input:\n{sample_query}\n\n"
            f"### Response:\n"
        )
        
        inputs = tokenizer(prompt, return_tensors="pt").to(device if torch.cuda.is_available() else "cpu")
        
        with torch.no_grad():
            output_tokens = peft_model.generate(
                **inputs,
                max_new_tokens=128,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            
        generated_text = tokenizer.decode(output_tokens[0], skip_special_tokens=True)
        logger.info("\n--- Inference Output ---\n" + generated_text + "\n" + "-" * 30)
    except Exception as e:
        logger.warning(f"Inference demo skipped or encountered notice: {e}")


def main():
    parser = argparse.ArgumentParser(description="QLoRA Fine-Tuning Pipeline for Causal LMs")
    parser.add_argument("--model_name", type=str, default="mistralai/Mistral-7B-v0.1", help="Base model identifier")
    parser.add_argument("--dataset_path", type=str, default="food_cs_queries.jsonl", help="Path to JSONL dataset")
    parser.add_argument("--output_dir", type=str, default="./lora-food-cs-adapter", help="Output directory for LoRA adapter")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=1, help="Per-device train batch size")
    parser.add_argument("--grad_accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    parser.add_argument("--max_length", type=int, default=512, help="Max sequence length")
    parser.add_argument("--lora_r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora_alpha", type=int, default=32, help="LoRA alpha scaling factor")
    parser.add_argument("--skip_inference", action="store_true", help="Skip post-training inference test")
    
    args = parser.parse_args()

    run_training(
        model_name=args.model_name,
        dataset_path=args.dataset_path,
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_length=args.max_length,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        do_test_inference=not args.skip_inference,
    )


if __name__ == "__main__":
    main()