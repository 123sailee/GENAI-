# WeekendYatri – Your Weekend Getaway Planner

**Student:** Sailee Abhale  
**Department:** CSE (Data Science)  
**Project ID:** SJ-54

## 1. Product

WeekendYatri is an AI-powered weekend travel recommendation assistant that suggests affordable 2-day trips across the Nashik–Ahilyanagar–Chhatrapati Sambhajinagar region.

It considers season, budget, travel time and travel preferences.

## 2. Target User

A group of four IT employees from Pune's Hinjewadi who get one free weekend every month and want affordable nature trips without visiting overcrowded destinations like Lonavala.

## 3. Problem Statement

Finding affordable weekend destinations is difficult because travel information is scattered across multiple websites. Travellers also struggle to identify the right season, estimate expenses and find reliable travel information.

## 4. Proposed Solution

WeekendYatri will:
- Recommend destinations based on season and budget.
- Suggest nature, religious and heritage destinations.
- Display season-fit badges.
- Provide travel and accommodation estimates.
- Provide destination information with official source links.

## 5. Data Sources

1. [Ahilyanagar District Tourism](https://ahilyanagar.maharashtra.gov.in/en/tourist-place/bhandardara/)
2. [Nashik District Tourism](https://nashik.gov.in/en/tourism/tourists-places)
3. Maharashtra Tourism
4. Wikivoyage

## 6. Technology Stack

- Python
- FastAPI
- Streamlit
- Pandas
- LangChain / LangGraph
- ChromaDB
- LLM APIs
- TF-IDF and cosine similarity
- Sentence Transformers (`all-MiniLM-L6-v2`)
- Groq API

## 7. Development Goal

Build a complete AI-powered travel assistant that helps users discover affordable, season-appropriate weekend getaways.

**Repository:** GENAI-  
**Developer:** Sailee Abhale

## 8. How to Run

### Prerequisites

- Python 3.11
- Git
- Groq API key

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd GENAI-
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
```

Keep your actual `.env` file private. Do not commit API keys to GitHub.

### 5. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

### 6. Open the API documentation

Visit:

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

The interactive Swagger documentation allows you to test the available API endpoints.

## 9. API Features

The FastAPI backend provides:

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Check API health |
| `/records` | GET | Retrieve destination records |
| `/records/{id}` | GET | Retrieve a destination by ID |
| `/search` | GET | Search destinations using TF-IDF |
| `/search/semantic` | GET | Search using semantic similarity |
| `/chat` | POST | Ask the AI travel assistant |
| `/questions` | POST | Submit travel questions |
| `/ask` | POST | Ask questions using retrieval-augmented generation |
| `/agent` | POST | Run the LangGraph-powered travel agent with RAG, cost estimation, memory and human approval |

## 10. RAG Evaluation and Configuration Comparison

The WeekendYatri RAG system was evaluated using 15 questions:

- 14 answerable questions
- 1 unanswerable question
- Embedding model: `all-MiniLM-L6-v2`
- Vector database: ChromaDB
- LLM: Groq

### Configuration Comparison

| Evaluation Metric | Configuration A | Configuration B |
|---|---:|---:|
| Chunk Size | 150 words | 300 words |
| Top-K | 3 | 5 |
| Stored Chunks | 22 | 21 |
| Retrieval Recall | 0.7381 | **0.9167** |
| Answer Keyword Coverage | 0.6667 | **0.7976** |
| Citation Coverage | **0.7444** | 0.6267 |
| Unknown Answer Accuracy | 1.0000 | 1.0000 |
| Average Response Time | 3.4645 sec | **1.2274 sec** |
| Overall Score | 0.7441 | **0.8313** |

### Selected Configuration

**Configuration B was selected as the winner.**

- Chunk size: 300 words
- Top-K: 5
- Overall score: 0.8313

Configuration B achieved better retrieval recall, answer keyword coverage and response time. Configuration A achieved higher citation coverage.

### Evaluation Method

The overall score uses the following weighted formula:

- Retrieval Recall: 40%
- Answer Keyword Coverage: 30%
- Citation Coverage: 20%
- Unknown Answer Accuracy: 10%

The overall score is a project-defined evaluation metric.

### Evaluation Files

- `eval/eval_set.json` – 15 evaluation questions.
- `eval/run_eval.py` – Evaluation script.
- `eval/rag_comparison.md` – Configuration comparison report.
- `eval/rag_eval_results.json` – Evaluation results.

## 11. Project Repository

The project source code, evaluation scripts and documentation are maintained in the **GENAI-** repository.
## 12. Day 9 – Agentic AI Workflow

WeekendYatri now includes an agentic AI workflow that combines RAG-based destination discovery, trip cost estimation, conversational memory and human approval.

### 12.1 Cost Estimation Tool

File: `app/tools.py`

The `weekend_trip_cost` tool estimates weekend trip expenses based on:

- Round-trip distance in kilometres
- Number of travellers
- Travel mode (own car or MSRTC bus)
- Stay budget per person
- Food budget per person

**Own Car Calculation:**

Transport Cost = (Round-trip Distance / Mileage) × Fuel Price

**MSRTC Bus Calculation:**

Transport Cost = Round-trip Distance × Applicable Fare per KM

The fare slabs are stored in `data/msrtc_fares.csv`. These are illustrative estimates, not official MSRTC tariffs.

The tool returns transport cost, stay cost, food cost, total group cost and cost per person.

### 12.2 Handwritten Agent

File: `app/agent_loop.py`

The hand-written agent identifies the user's request and selects the appropriate tool:

- RAG search for destination-related questions.
- `weekend_trip_cost` for trip expense calculations.

### 12.3 LangGraph Workflow

File: `app/graph.py`

The agent workflow is implemented using LangGraph and includes:

- Intent detection
- Conversation history and memory
- RAG retrieval
- Trip cost calculation
- Human approval checkpoint
- Approval and rejection handling

The workflow uses `MemorySaver` with thread IDs to maintain conversation state across requests.

### 12.4 Human Approval

Before calculating trip costs, the agent pauses and requests user approval.

- If approved, the cost calculation proceeds.
- If rejected, the calculation is not performed.

### 12.5 Agent API

Endpoint: `POST /agent`

The endpoint supports destination questions, trip cost estimation, conversation memory and approval-based execution.

Test the endpoint using the interactive Swagger documentation at:

`http://127.0.0.1:8000/docs`

### 12.6 Day 9 Files

- `app/tools.py` – Trip cost estimation tool.
- `app/agent_loop.py` – Handwritten agent implementation.
- `app/graph.py` – LangGraph workflow.
- `data/msrtc_fares.csv` – Illustrative MSRTC fare slabs.
- `app/main.py` – FastAPI agent endpoint.