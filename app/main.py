
import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.records import load_records
from app.smart_search import search_destinations
from app.llm import generate_response, load_system_prompt


app = FastAPI(
    title="WeekendYatri API",
    description="AI-powered weekend travel destination assistant",
    version="2.0.0"
)


# ---------- Request and Response Models ----------

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    retrieval_score: float = Field(ge=0, le=1)
    follow_up: str


# ---------- Existing API Endpoints ----------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "WeekendYatri API is running!"
    }


@app.get("/records")
def get_records(limit: int = 20):
    records = load_records()
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    for record in records:
        if record.id == record_id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Destination not found"
    )



@app.get("/search")
def search_records(q: str):
    results = search_destinations(
        q,
        top_n=20
    )

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }



# ---------- AI Chat Endpoint ----------

@app.post("/questions", response_model=ChatResponse)
@app.post("/chat", response_model=ChatResponse)
def chat_with_yatri(request: ChatRequest):

    # Step 1: Retrieve relevant destinations
    results = search_destinations(
        request.message,
        top_n=5
    )

    if not results:
        return ChatResponse(
            answer=(
                "I couldn't find matching destinations in my "
                "current database. Try mentioning a district, "
                "season, or destination category."
            ),
            retrieval_score=0.0,
            follow_up=(
                "Which district or type of destination interests you?"
            )
        )

    # Step 2: Calculate retrieval score in Python
    retrieval_score = max(
        item["similarity_score"] for item in results
    )

    # Step 3: Load complete destination information
    records = load_records()

    retrieved_places = {
        item["place"] for item in results
    }

    context_records = [
        record for record in records
        if record.place in retrieved_places
    ]

    # Step 4: Build context for the LLM
    context = [
        {
            "place": record.place,
            "district": record.district,
            "category": record.category,
            "best_season": record.best_season,
            "how_to_reach": record.how_to_reach,
            "source_url": record.source_url,
            "official_details": record.official_details
        }
        for record in context_records
    ]

    # Step 5: Prepare the grounded prompt
    system_prompt = load_system_prompt()

    user_message = f"""
Retrieved destination information:

{json.dumps(context, ensure_ascii=False, indent=2)}

User question:
{request.message}

Use only the retrieved information to answer.
Return the required JSON response with answer and follow_up.
Do not include a confidence or retrieval score.
"""

    # Step 6: Generate AI response
    try:
        llm_response = generate_response(
            system_prompt,
            user_message
        )

        parsed_response = json.loads(llm_response)

        return ChatResponse(
            answer=parsed_response["answer"],
            retrieval_score=retrieval_score,
            follow_up=parsed_response["follow_up"]
        )

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid response from AI model: {str(error)}"
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(error)}"
        )
