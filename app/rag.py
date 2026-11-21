import json
import os

from app.llm import generate_response
from app.records import load_records
from app.smart_search import search_destinations
from app.vectorstore import semantic_search

RAG_SYSTEM_PROMPT = """
You are WeekendYatri, a travel information assistant.

Answer the user's question using ONLY the retrieved context.

STRICT RULES:
1. Do not use outside knowledge or invent facts.
2. If the retrieved context does not contain enough information
   to answer the question, respond exactly: "I don't know".
3. Never invent prices, bus fares, timings, distances or facilities.
4. Support factual claims with citations.
5. Use the source URL provided in the retrieved metadata.
6. Include a page number only if actual page metadata is available.
7. Do not invent page numbers.
8. If the context is irrelevant, respond: "I don't know".
9. Return valid JSON only.

Required JSON structure:
{
    "answer": "Your grounded answer with citations.",
    "citations": [
        {
            "title": "Destination title",
            "source_url": "Source URL",
            "page": null
        }
    ]
}

If you do not know the answer, return:
{
    "answer": "I don't know",
    "citations": []
}
"""


def _retrieve_lightweight(question: str, top_k: int = 5) -> list[dict]:
    """Low-memory TF-IDF/keyword retrieval fallback for <=512 MB containers."""
    matches = search_destinations(question, top_n=top_k)
    if not matches:
        return []

    records_by_place = {record.place: record for record in load_records()}
    retrieved_chunks = []

    for item in matches:
        place = item.get("place", "")
        record = records_by_place.get(place)
        if not record:
            continue

        content = (
            f"{record.place} ({record.district}, {record.category}). "
            f"Best season: {record.best_season}. "
            f"How to reach: {record.how_to_reach}. "
            f"Details: {record.official_details}"
        )
        similarity = float(item.get("similarity_score", 0.0))
        retrieved_chunks.append({
            "content": content,
            "title": record.place,
            "district": record.district,
            "category": record.category,
            "source_url": record.source_url,
            "page": None,
            "cosine_distance": round(max(0.0, 1.0 - similarity), 4),
        })

    return retrieved_chunks


def retrieve_context(question, top_k=5):
    """Retrieve relevant destination chunks from ChromaDB or lightweight retriever."""
    if os.getenv("USE_LIGHTWEIGHT_RETRIEVAL", "").lower() in {"1", "true", "yes"}:
        return _retrieve_lightweight(question=question, top_k=top_k)

    results = semantic_search(query=question, top_k=top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved_chunks = []

    for index, document in enumerate(documents):
        metadata = metadatas[index]
        retrieved_chunks.append({
            "content": document,
            "title": metadata.get("title", "Unknown"),
            "district": metadata.get("district", "Unknown"),
            "category": metadata.get("category", "Unknown"),
            "source_url": metadata.get("source_url", ""),
            "page": metadata.get("page"),
            "cosine_distance": float(distances[index]),
        })

    return retrieved_chunks


def ask_question(question, top_k=5):
    """
    Answer a question using retrieved chunks
    and Groq, with source citations.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if top_k < 1 or top_k > 20:
        raise ValueError("top_k must be between 1 and 20.")

    retrieved_chunks = retrieve_context(
        question=question.strip(),
        top_k=top_k,
    )

    if not retrieved_chunks:
        return {
            "answer": "I don't know",
            "citations": [],
            "retrieved_chunks": [],
        }

    context = json.dumps(retrieved_chunks, ensure_ascii=False, indent=2)

    user_message = f"""
Retrieved context:

{context}

User question:
{question}

Answer using only the retrieved context.

Remember:
- Do not invent information.
- If the context does not answer the question, return "I don't know".
- Cite the sources used.
- Return valid JSON only.
"""

    response = generate_response(RAG_SYSTEM_PROMPT, user_message)

    try:
        parsed_response = json.loads(response)
    except json.JSONDecodeError:
        return {
            "answer": "I don't know",
            "citations": [],
            "retrieved_chunks": retrieved_chunks,
        }

    answer = parsed_response.get("answer", "I don't know")
    citations = parsed_response.get("citations", [])

    if not isinstance(answer, str) or not isinstance(citations, list):
        answer = "I don't know"
        citations = []

    valid_sources = {
        (chunk["title"], chunk["source_url"])
        for chunk in retrieved_chunks
        if chunk["source_url"]
    }

    validated_citations = []
    for citation in citations:
        if not isinstance(citation, dict):
            continue

        title = citation.get("title")
        source_url = citation.get("source_url")

        if (title, source_url) not in valid_sources:
            continue

        validated_citations.append({
            "title": title,
            "source_url": source_url,
            "page": None,
        })

    if answer.strip().lower() == "i don't know":
        answer = "I don't know"
        validated_citations = []
    elif not validated_citations:
        answer = "I don't know"

    return {
        "answer": answer,
        "citations": validated_citations,
        "retrieved_chunks": retrieved_chunks,
    }
