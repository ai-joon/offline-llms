import torch, os
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig
from trl import SFTTrainer

base_model = os.environ.get("BASE_MODEL", "Qwen/Qwen2.5-0.5B-Instruct")  # Much smaller model for quick testing
data_path  = os.environ.get("DATA_PATH",  "data.jsonl")  # your JSONL
out_dir    = os.environ.get("OUT_DIR",   "qwen2.5-3b-lora")

use_cuda = torch.cuda.is_available()

# 4-bit load for QLoRA (CUDA only). Disable on CPU to avoid bitsandbytes errors.
bnb_cfg = (BitsAndBytesConfig(load_in_4bit=True,
                             bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
           if use_cuda else None)

tok = AutoTokenizer.from_pretrained(base_model, use_fast=True, trust_remote_code=True)
tok.pad_token = tok.eos_token

model = AutoModelForCausalLM.from_pretrained(
    base_model,
    quantization_config=bnb_cfg,
    attn_implementation="flash_attention_2" if use_cuda else None,
    low_cpu_mem_usage=not use_cuda,
    trust_remote_code=True,
    torch_dtype=torch.bfloat16 if use_cuda else torch.float32,
    device_map=("auto" if use_cuda else None),
)

# LoRA config (simplified for quick testing)
lora = LoraConfig(
    r=8, lora_alpha=16, lora_dropout=0.1, bias="none",  # Reduced rank and alpha
    task_type="CAUSAL_LM",
    target_modules=["q_proj","v_proj"],  # Fewer target modules
)

# Format function for JSONL {"prompt","response"}
def fmt(samples):
    out = []
    for p, r in zip(samples["prompt"], samples["response"]):
        out.append(f"### Instruction:\n{p}\n\n### Response:\n{r}")
    return {"text": out}

ds = load_dataset("json", data_files=data_path, split="train")
ds = ds.map(fmt, batched=True, remove_columns=ds.column_names)

args = TrainingArguments(
    output_dir=out_dir,
    num_train_epochs=0.1,  # Just 10% of one epoch for quick testing
    per_device_train_batch_size=2,  # Increased batch size
    gradient_accumulation_steps=2,  # Reduced for faster training
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.1,
    logging_steps=1,  # Log every step
    save_steps=50,  # Save more frequently
    bf16=use_cuda,
    fp16=False,
    max_grad_norm=0.3,
    gradient_checkpointing=False,  # Disabled for speed
    max_steps=10,  # Limit to just 10 steps for quick test
    optim="adamw_torch",
    dataloader_pin_memory=False,
    report_to=["none"],
)

trainer = SFTTrainer(
    model=model,
    peft_config=lora,
    train_dataset=ds,
    # tokenizer=tok,
    args=args,
)
trainer.train()
trainer.model.save_pretrained(out_dir)
tok.save_pretrained(out_dir)
