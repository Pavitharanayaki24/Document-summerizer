# Backend setup: changes to get the app running

This document summarizes what was changed while setting up the Document Summarizer **Flask backend** on Windows (fresh clone, Python 3.10 venv).

## Environment

- **Python:** 3.10 in a virtual environment under `backend/.venv`.
- **Required secret:** Create `backend/.env` with `GROQ_API_KEY=<your Groq API key>` (used in `Fetching/query.py` for chat completions via Groq’s OpenAI-compatible API).
- **Optional:** `HF_TOKEN=<Hugging Face token>` in the same file for higher Hugging Face Hub rate limits and fewer anonymous-download warnings when the embedding model is fetched.

## Pip / venv notes

- **`pip install --upgrade pip` on Windows** sometimes fails with **Access is denied (WinError 5)** during pip’s self-upgrade. If that happens, **skip upgrading pip** and use the venv’s bundled pip (e.g. `python -m pip install -r requirements.txt`).
- If the venv ends up broken after a failed pip self-upgrade, **delete `.venv` and recreate** it with `python -m venv .venv`, then reinstall dependencies.

## `requirements.txt` edits

The file was originally a very large `pip freeze`. A few pins were fixed so installs work on **PyPI + Python 3.10 + Windows**.

### Why each change

| Change | Reason |
|--------|--------|
| `networkx==3.5` → `networkx==3.4.2` | `networkx` 3.5 requires Python 3.11+; 3.4.2 is compatible with Python 3.10. |
| `torch==2.9.0+cpu` / `torchvision==0.24.0+cpu` → `torch==2.9.0` / `torchvision==0.24.0` | The `+cpu` builds are published on PyTorch’s wheel index, not the default PyPI index used by `pip install -r requirements.txt`. |
| Removed `vboxapi==1.0` | Not published on PyPI (VirtualBox-related); it was an accidental freeze artifact. |
| Added `langchain-huggingface>=0.1.0` | Supports the updated `HuggingFaceEmbeddings` import (see below). |

**Python version used when resolving these:** **3.10** (venv). `networkx` **3.5** only supports **Python ≥3.11**, which is why it was downgraded to **3.4.2**.

## Code changes

- **`Fetching/query.py`** and **`Fetching/gather.py`:**  
  `HuggingFaceEmbeddings` is imported from **`langchain_huggingface`** instead of `langchain_community.embeddings`, to match LangChain’s current direction and avoid deprecation warnings.

## Runtime behavior (not code changes)

- First run downloads the **sentence-transformers** embedding model (`sentence-transformers/all-MiniLM-L6-v2`) into the Hugging Face cache; progress bars and occasional **BertModel LOAD REPORT** messages are expected.
- **`python app.py`** runs Flask with **`debug=True`**, which enables the **reloader** (the process may start twice, and the embedding model may load twice in development).
- The development server warning (“Do not use it in production”) is normal until you deploy with a production WSGI server.

## How to run

```powershell
cd backend
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

Server default: **http://127.0.0.1:8000** (matches the frontend’s axios URLs).

Before using **`POST /ask`**, upload a document with **`POST /upload`** so `Fetching/vector_store` exists.

---

## What changed → what we use now (summary only)

Use this section as a quick checklist; details are above.

**`requirements.txt` (version pins)**

- `networkx`: **3.5** → **3.4.2**
- `torch`: **2.9.0+cpu** → **2.9.0**
- `torchvision`: **0.24.0+cpu** → **0.24.0**
- `vboxapi`: **1.0** → **removed**
- `langchain-huggingface`: *(none)* → **`>=0.1.0`** (added)

**Code**

- `HuggingFaceEmbeddings` import: **`langchain_community.embeddings`** → **`langchain_huggingface`** (`Fetching/query.py`, `Fetching/gather.py`)


from langchain_huggingface import HuggingFaceEmbeddings # type: ignore
