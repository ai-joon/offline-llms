## Running Offline LLMs

This repo contains a local RAG demo, a Streamlit chatbot UI, utilities to build and reuse a FAISS vector DB, and LoRA fine-tuning/merge helpers.

### Prerequisites
- Python 3.11+ (tested on Windows 10)
- Ollama running locally (`http://localhost:11434`)
- Recommended shell: Windows PowerShell

### Install dependencies
```powershell
python -m pip install -r requirements.txt
```

### Pull required Ollama models
```powershell
ollama pull nomic-embed-text
ollama pull qwen2.5:0.5b-instruct
```

---

## Build a FAISS vector database (loader.py)
`loader.py` loads PDF(s), splits and sanitizes text, embeds with Ollama, and saves a FAISS index to disk.

Examples:
```powershell
# Single PDF → saved to .\faiss_index
python .\loader.py --pdf C:\Source\research\docx\report-ko.pdf --out C:\Source\research\faiss_index --emb nomic-embed-text --base http://localhost:11434

# All PDFs in a folder
python .\loader.py --dir C:\Source\research\docx --out C:\Source\research\faiss_index --emb nomic-embed-text --base http://localhost:11434
```

Notes:
- Text is sanitized to remove invalid surrogate characters to avoid JSON encoding errors in the Ollama client.
- Default chunking is 250/50 (size/overlap). Adjust in `loader.py` if desired.
- The output directory contains FAISS index files that can be reloaded later without recomputing embeddings.

---

## Run the Streamlit RAG chatbot (interface.py)
`interface.py` provides a dark-mode chat UI with chat history, retrieval controls, source panel, and an embedded PDF viewer with pagination.

```powershell
streamlit run interface.py
```

Behavior:
- On startup, the app auto-loads a FAISS index from `FAISS_INDEX_DIR` or `./faiss_index` if present.
- Uses Ollama locally with defaults below; you can override via environment variables.
- Right panel shows the original PDF (picker + viewer). Pagination controls are centered at the bottom of the viewer.

Environment variables (optional):
- `FAISS_INDEX_DIR` → path to a saved FAISS index (default `./faiss_index`)
- `OLLAMA_HOST` → e.g., `http://localhost:11434`
- `OLLAMA_EMBED` → embedding model tag (default `nomic-embed-text`)
- `OLLAMA_LLM` → chat model tag (default `qwen2.5:0.5b-instruct`)

---

## Minimal RAG script (main.py)
`main.py` shows a minimal RAG flow using a prebuilt FAISS index.

Edit the index path in `main.py` if needed:
```python
INDEX_DIR = r"C:\\Source\\research\\faiss_index"
```
Run:
```powershell
python .\main.py
```

---

## Fine-tuning with LoRA (train.py)
Quick demonstration fine-tune using TRL.

Input data format: `data.jsonl` lines with keys `prompt` and `response`.
```json
{"prompt": "...", "response": "..."}
```

Run:
```powershell
python .\train.py
```
Outputs are written to `OUT_DIR` (default `qwen2.5-3b-lora`). See code for tunables.

---

## Merge LoRA into a base model (merge.py)
Creates a merged Hugging Face folder you can use directly or export to GGUF.

Examples:
```powershell
# Merge only
python .\merge.py --base Qwen/Qwen2.5-3B-Instruct --adapter C:\Source\research\qwen2.5-3b-lora --out C:\Source\research\qwen2.5-3b-merged --cpu-only --dtype fp32

# Merge and test generation
python .\merge.py --base Qwen/Qwen2.5-0.5B-Instruct --adapter C:\Source\research\qwen2.5-3b-lora --out C:\Source\research\qwen2.5-3b-merged --cpu-only --dtype fp32 --infer
```

Key flags:
- `--base` HF base model id/path
- `--adapter` LoRA adapter folder
- `--out` Output HF folder for merged model
- `--cpu-only` Force CPU load/merge (safer on Windows without CUDA)
- `--dtype` fp32 (default) or bf16
- `--offload` Temp folder to reduce RAM usage while loading

---

## Troubleshooting
- Ollama model not found: `ollama pull <model>` and confirm server at `OLLAMA_HOST`.
- UnicodeEncodeError while embedding: handled by sanitization in `loader.py` (rebuild the index).
- PDF preview blank: install PyMuPDF for the image-based viewer:
  ```powershell
  pip install pymupdf
  ```
- Performance: in the UI lower Top-k, `Max context size`, and `Max answer tokens`, or use smaller models.


