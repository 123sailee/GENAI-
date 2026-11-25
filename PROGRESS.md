# WeekendYatri — Project Progress & Release Checklist

**Status:** Complete (`final` release tagged and deployed to `https://weekendyatri.onrender.com`)

## Milestones & Deliverables

- [x] **D1–D2: Project Scoping & Curated Dataset** — Collected and deduplicated Maharashtra weekend getaway records across district government portals, state tourism sites, and Wikivoyage (`Aurangabad` -> `Chhatrapati Sambhajinagar`, `Ahmednagar` -> `Ahilyanagar`, `Randha` / `Randhha`) with seasonal rules and MSRTC fare CSVs.
- [x] **D3–D4: FastAPI Service & Core Endpoints** — Implemented `/health`, `/records`, `/search`, `/ask`, `/chat`, `/agent`, and `/metrics` with Pydantic validation schemas.
- [x] **D5–D6: Embeddings & Vector Search** — Built semantic chunking and ChromaDB indexing using `all-MiniLM-L6-v2` alongside a lightweight TF-IDF fallback (`USE_LIGHTWEIGHT_RETRIEVAL=true`) for 512 MB cloud containers.
- [x] **D7–D8: Grounded RAG & Citation Verification** — Integrated Groq LLM (`openai/gpt-oss-20b`) with strict JSON grounding, programmatic `source_url` validation, and `"I don't know"` abstention on out-of-scope questions.
- [x] **D9–D10: LangGraph Agent & Deterministic Cost Tools** — Built stateful multi-turn trip planning with a Human-in-the-Loop (HITL) approval gate and deterministic `own_car` vs. `msrtc_bus` fare, stay, and meal calculators.
- [x] **D11: Automated Testing & CI** — Configured GitHub Actions (`ruff check .` and `pytest -v` with 13 passing unit/integration tests).
- [x] **D12: Docker & Live Render Deployment** — Containerized application, lazy-loaded heavy vector dependencies (cutting cold-start RSS from 596 MB to 209 MB), and deployed live at `https://weekendyatri.onrender.com`.
- [x] **D13: Observability, Security & Portfolio README** — Added SHA-256 LRU+TTL caching (`0.04 ms` cache hit vs. `727.32 ms` uncached), `/metrics` telemetry, prompt-injection `HTTP 400` guardrails, 15-query benchmark results (`0.9167` recall, `0.8313` weighted score), live demo video link, and `docs/resume.md`.
- [x] **D14: Interview Prep & Final Release Tag** — Authored `docs/interview.md` (60-second pitch, STAR hardest-problem story, and 10 technical Q&As), rehearsed end-to-end live demo twice, closed all checklist items in `PROGRESS.md`, and tagged `final`.