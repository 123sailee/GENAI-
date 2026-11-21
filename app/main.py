import json
import logging
import time

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.graph import run_graph_agent
from app.llm import METRICS, generate_response, load_system_prompt
from app.rag import ask_question
from app.records import load_records
from app.security import validate_safe_input
from app.smart_search import search_destinations
from app.vectorstore import semantic_search as search_semantically

logger = logging.getLogger("weekendyatri.api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="WeekendYatri API",
    description="AI-powered weekend travel destination assistant",
    version="2.4.0",
)


@app.middleware("http")
async def log_request_latency(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(latency_ms)
    logger.info(
        "http_request method=%s path=%s status=%d latency_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        latency_ms,
    )
    return response


# ---------- Request and Response Models ----------

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    retrieval_score: float = Field(ge=0, le=1)
    follow_up: str


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    answer: str
    citations: list[dict]
    retrieved_chunks: list[dict]


class AgentRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1000)
    thread_id: str = Field(min_length=1, max_length=100)

    round_trip_km: float | None = Field(default=None, gt=0, le=5000)
    people: int | None = Field(default=None, ge=1, le=50)
    mode: str | None = Field(default=None, max_length=32)

    stay_per_person: float = Field(default=0, ge=0, le=100000)
    food_per_person: float = Field(default=0, ge=0, le=50000)

    mileage_kmpl: float | None = Field(default=None, gt=0, le=100)
    fuel_price_per_litre: float | None = Field(default=None, gt=0, le=500)

    approved: bool | None = None


# ---------- Health & Observability Endpoints ----------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "WeekendYatri API is running!",
    }


@app.get("/metrics")
def get_metrics():
    return {
        "status": "ok",
        "llm_metrics": METRICS,
    }


@app.get("/records")
def get_records(limit: int = Query(default=20, ge=1, le=100)):
    records = load_records()
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    for record in records:
        if record.id == record_id:
            return record

    raise HTTPException(status_code=404, detail="Destination not found")


@app.get("/search")
def search_records(q: str = Query(min_length=1, max_length=300)):
    try:
        safe_q = validate_safe_input(q, max_chars=300)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    results = search_destinations(safe_q, top_n=20)
    return {
        "query": safe_q,
        "total_results": len(results),
        "results": results,
    }


# ---------- Semantic Search Endpoint ----------

@app.get("/search/semantic")
def semantic_search_records(
    q: str = Query(min_length=2, max_length=500),
    top_k: int = Query(default=5, ge=1, le=20),
):
    """Search destinations using sentence embeddings and ChromaDB."""
    try:
        safe_q = validate_safe_input(q, max_chars=500)
        results = search_semantically(query=safe_q, top_k=top_k)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted_results = []
        for index, document in enumerate(documents):
            metadata = metadatas[index]
            formatted_results.append({
                "rank": index + 1,
                "title": metadata.get("title"),
                "district": metadata.get("district"),
                "category": metadata.get("category"),
                "best_season": metadata.get("best_season"),
                "source_url": metadata.get("source_url"),
                "cosine_distance": round(float(distances[index]), 4),
                "document": document,
            })

        return {
            "query": safe_q,
            "total_results": len(formatted_results),
            "search_type": "semantic",
            "results": formatted_results,
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Semantic search service error: {str(error)}",
        )


# ---------- AI Chat Endpoint ----------

@app.post("/questions", response_model=ChatResponse)
@app.post("/chat", response_model=ChatResponse)
def chat_with_yatri(request: ChatRequest):
    try:
        safe_message = validate_safe_input(request.message, max_chars=1000)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    results = search_destinations(safe_message, top_n=5)

    if not results:
        return ChatResponse(
            answer=(
                "I couldn't find matching destinations in my "
                "current database. Try mentioning a district, "
                "season, or destination category."
            ),
            retrieval_score=0.0,
            follow_up="Which district or type of destination interests you?",
        )

    retrieval_score = max(item["similarity_score"] for item in results)
    records = load_records()
    retrieved_places = {item["place"] for item in results}

    context_records = [
        record for record in records if record.place in retrieved_places
    ]

    context = [
        {
            "place": record.place,
            "district": record.district,
            "category": record.category,
            "best_season": record.best_season,
            "how_to_reach": record.how_to_reach,
            "source_url": record.source_url,
            "official_details": record.official_details,
        }
        for record in context_records
    ]

    system_prompt = load_system_prompt()
    user_message = f"""
Retrieved destination information:

{json.dumps(context, ensure_ascii=False, indent=2)}

User question:
{safe_message}

Use only the retrieved information to answer.
Return the required JSON response with answer and follow_up.
Do not include a confidence or retrieval score.
"""

    try:
        llm_response = generate_response(system_prompt, user_message)
        parsed_response = json.loads(llm_response)

        return ChatResponse(
            answer=parsed_response["answer"],
            retrieval_score=retrieval_score,
            follow_up=parsed_response["follow_up"],
        )

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid response from AI model: {str(error)}",
        )

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {str(error)}",
        )


# ---------- Retrieval-Augmented Generation API ----------

@app.post("/ask", response_model=AskResponse)
def ask_weekendyatri(request: AskRequest):
    """Answer questions using retrieved ChromaDB chunks, Groq, and citations."""
    try:
        safe_question = validate_safe_input(request.question, max_chars=1000)
        result = ask_question(question=safe_question, top_k=request.top_k)

        return AskResponse(
            answer=result["answer"],
            citations=result["citations"],
            retrieved_chunks=result["retrieved_chunks"],
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"RAG service error: {str(error)}",
        )


# ---------- LangGraph Agent API ----------

@app.post("/agent")
def weekendyatri_agent(request: AgentRequest):
    """Run the LangGraph WeekendYatri agent."""
    try:
        safe_message = validate_safe_input(request.message, max_chars=1000)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    message_lower = safe_message.lower()
    cost_keywords = [
        "cost",
        "budget",
        "expense",
        "calculate",
        "estimate",
        "price",
        "afford",
    ]
    wants_cost = any(keyword in message_lower for keyword in cost_keywords)

    if wants_cost and request.approved is not True and request.approved is not False:
        if (
            request.round_trip_km is None
            or request.people is None
            or request.mode is None
        ):
            raise HTTPException(
                status_code=400,
                detail="Cost calculation requires round_trip_km, people and mode.",
            )

        if request.mode not in ("own_car", "msrtc_bus"):
            raise HTTPException(
                status_code=400,
                detail="Mode must be own_car or msrtc_bus.",
            )

        if request.mode == "own_car":
            if (
                request.mileage_kmpl is None
                or request.fuel_price_per_litre is None
            ):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Own car calculation requires "
                        "mileage_kmpl and fuel_price_per_litre."
                    ),
                )

    try:
        result = run_graph_agent(
            message=safe_message,
            thread_id=request.thread_id,
            round_trip_km=request.round_trip_km,
            people=request.people,
            mode=request.mode,
            stay_per_person=request.stay_per_person,
            food_per_person=request.food_per_person,
            mileage_kmpl=request.mileage_kmpl,
            fuel_price_per_litre=request.fuel_price_per_litre,
            approved=request.approved,
        )

        return {
            "agent": "WeekendYatri",
            **result,
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution error: {str(error)}",
        )
