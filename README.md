# WeekendYatri — AI Weekend Travel & Trip-Cost Assistant

[![CI](https://github.com/123sailee/GENAI-/actions/workflows/ci.yml/badge.svg)](https://github.com/123sailee/GENAI-/actions/workflows/ci.yml)

**WeekendYatri** is a production-ready Retrieval-Augmented Generation (RAG) and LangGraph travel-planning API for Maharashtra weekend getaways (Nashik, Bhandardara, Ahilyanagar, and surrounding destinations). It grounds answers in curated tourism sources with verifiable citations and computes transparent trip budgets with human-in-the-loop approval.

## Live Deployment & Demo

- **Live Deployment (Render):** https://weekendyatri.onrender.com
- **Public Health Check:** https://weekendyatri.onrender.com/health
- **Interactive API Docs (Swagger UI):** https://weekendyatri.onrender.com/docs
- **Live Metrics Endpoint:** https://weekendyatri.onrender.com/metrics
- **Demo Video Walkthrough:** [Watch 90-Second Demo Video](https://drive.google.com/file/d/1PoC_7PolAYYHmrj6wtiyDWS2j_jIToBI/view?usp=sharing)

---

## Problem Statement

Planning a 1–2 day regional trip in Maharashtra typically requires cross-referencing scattered state tourism pages, MSRTC bus fare tables, seasonal travel advisories, and manual fuel/stay spreadsheets—while generic LLMs frequently hallucinate routes, distances, or ticket prices. **WeekendYatri** solves this by:
1. Grounding every destination answer in chunked, embedded regional tourism records stored in **ChromaDB** with explicit source citations and abstention on out-of-scope questions.
2. Combining semantic retrieval with a **LangGraph** stateful workflow that pauses for explicit user approval before running deterministic transport (`own_car` vs. `msrtc_bus`), stay, and food cost tools.

---

## System Architecture

```mermaid
flowchart TD
    Client[Client / Swagger UI] --> Guard[FastAPI Middleware & Input / Injection Guard]
    Guard --> Router{Endpoint Router}

    Router -->|GET /search/semantic| VS[ChromaDB + all-MiniLM-L6-v2]
    Router -->|POST /ask| Cache{LRU + TTL Response Cache}
    Router -->|POST /agent| Agent[LangGraph Stateful Agent]

    Cache -->|Cache Hit 0.04 ms| Metrics[Latency & Token Logger /metrics]
    Cache -->|Cache Miss| RAG[RAG Pipeline: Top-5 Retrieval + Citations]
    RAG --> VS
    RAG --> Groq[Groq Chat Completions API]
    Groq --> Metrics

    Agent -->|Destination Query| RAG
    Agent -->|Cost Query| HITL{Human Approval Gate}
    HITL -->|Approved| Tools[Cost Calculator & MSRTC Fare CSV]
    Tools --> Metrics
    Metrics --> Client
---

## Results

Evaluated on a 15-question benchmark (14 answerable destination queries + 1 out-of-scope unanswerable query) using `all-MiniLM-L6-v2`, ChromaDB, and Groq:

| Metric | Config A (`chunk=150, top_k=3`) | Config B (`chunk=300, top_k=5`) | Improvement |
|---|---:|---:|---:|
| **Stored Chunks** | 22 | 21 | Compact index |
| **Retrieval Recall (40% weight)** | 0.7381 | **0.9167** | **+24.2%** |
| **Answer Keyword Coverage (30% weight)** | 0.6667 | **0.7976** | **+19.6%** |
| **Citation Coverage (20% weight)** | **0.7444** | 0.6267 | -15.8% |
| **Unknown Answer Accuracy (10% weight)** | 1.0000 | **1.0000** | 100% abstention |
| **Average Response Time** | 3.4645 s | **1.2274 s** | **64.6% faster** |
| **Weighted Overall Score** | 0.7441 | **0.8313** | **+11.7%** |

---

## Production notes

Measured directly on the live Render deployment (`[https://weekendyatri.onrender.com](https://weekendyatri.onrender.com)`) and local benchmarks:

- **Measured Live Latency (Uncached vs. Cached):** On `POST /ask`, an uncached Groq completion (`openai/gpt-oss-20b`) takes **727.32 ms** (`1,227.4 ms` average across the 15-question benchmark), whereas a repeated query served from the in-memory LRU/TTL cache returns in **0.04 ms** (**99.99% latency reduction**).
- **Measured Token Usage & Cache Hit Rate:** A single uncached `/ask` request consumes **1,479 total tokens** (**1,344 prompt tokens** + **135 completion tokens**); identical follow-up requests achieve a **100% cache hit** (`cache_hits: 1`, `cache_misses: 1`, **0 additional tokens**), tracked live at `GET /metrics`.
- **Memory Footprint & 512 MB Cloud Optimization:** Lazy-importing `sentence-transformers` and `chromadb` keeps cold-start RSS memory at **209 MB** (vs. **596 MB** with PyTorch + ChromaDB loaded). Enabling `USE_LIGHTWEIGHT_RETRIEVAL=true` in `Dockerfile` keeps live Render memory well under its **512 MB** free-tier RAM limit.
- **Input Limits & Security Guardrails:** Pydantic enforces strict request bounds (`question`/`message` `2–1,000` chars, `search` query `<=300` chars, `top_k` `1–20`, `limit` `1–100`, `round_trip_km` `<=5,000`), and `app/security.py` blocks prompt-injection / system-prompt extraction payloads with `HTTP 400`.

---

## Local Setup & Testing

1. Create and activate a virtual environment: `python -m venv .venv && .venv\Scripts\Activate.ps1`
2. Install dependencies and add `GROQ_API_KEY` to `.env`: `pip install -r requirements.txt`
3. Start the server: `uvicorn app.main:app --reload --port 8000`
4. Run lint and unit tests: `ruff check . && pytest -v`
