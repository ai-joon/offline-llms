import argparse
import os
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from peft import PeftModel

parser = argparse.ArgumentParser(description="Merge a PEFT LoRA adapter into a base HF model and optionally test inference.")
parser.add_argument("--base", default=os.environ.get("HF_BASE_ID", "Qwen/Qwen2.5-3B-Instruct"), help="Base HF model id or path")
parser.add_argument("--adapter", default=os.environ.get("LORA_DIR", "./qwen2.5-3b-lora"), help="Path to PEFT LoRA directory")
parser.add_argument("--out", default=os.environ.get("MERGED_OUT", "./qwen2.5-3b-merged"), help="Output directory for merged model")
parser.add_argument("--infer", action="store_true", help="After merging, reload merged model and run a small generation test")
parser.add_argument("--offload", default=str(Path.cwd() / "_offload"), help="Folder to offload weights during load (reduces RAM spikes)")
parser.add_argument("--cpu-only", action="store_true", help="Force CPU device map for loading/merging")
parser.add_argument("--dtype", choices=["fp32", "bf16"], default="fp32", help="Load dtype for base (CPU: fp32 recommended)")
args = parser.parse_args()

base = args.base
adapter = args.adapter
merged = args.out
offload_dir = Path(args.offload)
force_cpu = args.cpu_only
load_dtype = torch.float32 if args.dtype == "fp32" else (torch.bfloat16 if torch.cuda.is_available() and not args.cpu_only else torch.float32)
offload_dir.mkdir(parents=True, exist_ok=True)

# --- 1) merge LoRA into full weights ---
print("Loading base model to merge LoRA (this can take a while)...", flush=True)
device_map = "cpu" if force_cpu else ("auto" if torch.cuda.is_available() else "cpu")
m = AutoModelForCausalLM.from_pretrained(
    base,
    trust_remote_code=True,
    torch_dtype=load_dtype,
    device_map=device_map,
    low_cpu_mem_usage=True,
    offload_folder=str(offload_dir),
)
print("Base model loaded.", flush=True)

print("Loading PEFT adapter...", flush=True)

from peft import PeftConfig

# Load PEFT adapter without training and merge
peft_cfg = PeftConfig.from_pretrained(adapter)
peft_type = getattr(peft_cfg, "peft_type", None)
is_lora = False
if peft_type is not None:
    try:
        # peft_type may be an enum (e.g., PeftType.LORA) or a string
        name = peft_type.name if hasattr(peft_type, "name") else str(peft_type)
        is_lora = str(name).upper().endswith("LORA")
    except Exception:
        is_lora = False
if not is_lora:
    print(f"Warning: adapter at {adapter} reports peft_type={peft_type}, proceeding anyway...", flush=True)

m = PeftModel.from_pretrained(
    m,
    adapter,
    is_trainable=False,
    adapter_name="default",
)
m = m.merge_and_unload()
print("Saving merged model to:", merged, flush=True)
m.save_pretrained(merged, safe_serialization=True)

# --- 2) save tokenizer alongside merged weights (so merged dir is self-contained) ---
tok = AutoTokenizer.from_pretrained(base, use_fast=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
tok.save_pretrained(merged)

if args.infer:
    # --- 3) reload merged model for inference (GPU if available) ---
    print("Reloading merged model for inference...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        merged,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        low_cpu_mem_usage=True,
        offload_folder=str(offload_dir),
    )

    tokenizer = AutoTokenizer.from_pretrained(merged, use_fast=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Optional: a sensible generation config
    gen_cfg = GenerationConfig(
        max_new_tokens=128,
        temperature=0.2,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.05,
    )

    # --- 4) generate (use the same format you trained with) ---
    user_instruction = "Explain RAFT consensus in two short sentences."
    prompt = f"### Instruction:\n{user_instruction}\n\n### Response:\n"

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    print("Generating...", flush=True)
    with torch.inference_mode():
        output = model.generate(
            **inputs,
            generation_config=gen_cfg,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )

    text = tokenizer.decode(output[0], skip_special_tokens=True)
    print("\n=== Model output ===\n", flush=True)
    print(text, flush=True)
else:
    print("Merge complete. Skipping inference (run with --infer to test generation).", flush=True)

