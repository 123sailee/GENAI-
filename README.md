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