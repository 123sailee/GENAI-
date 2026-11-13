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

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

The interactive Swagger documentation allows you to test the available API endpoints.