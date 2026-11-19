
import json
import re
import time
from pathlib import Path

import chromadb

from app.llm import generate_response
from app.vectorstore import get_model

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = BASE_DIR / "data" / "rag_eval_db"
DATASET_FILE = BASE_DIR / "eval" / "eval_set.json"
PROGRESS_FILE = BASE_DIR / "eval" / "rag_eval_progress.json"
RESULTS_FILE = BASE_DIR / "eval" / "rag_eval_results.json"
REPORT_FILE = BASE_DIR / "eval" / "rag_comparison.md"


CONFIG_B = {
    "name": "Configuration B",
    "chunk_size": 300,
    "top_k": 5,
    "collection_name": "weekendyatri_rag_300"
}


# Previously completed and measured Configuration A.
# Values are taken from the user's completed terminal evaluation.
CONFIG_A_METRICS = {
    "configuration": "Configuration A",
    "chunk_size": 150,
    "top_k": 3,
    "collection_count": 22,
    "retrieval_recall": 0.7381,
    "answer_keyword_coverage": 0.6667,
    "citation_coverage": 0.7444,
    "unknown_answer_accuracy": 1.0,
    "average_response_time_seconds": 3.4645,
    "overall_score": 0.7441
}


SYSTEM_PROMPT = """
You are WeekendYatri, a travel information assistant.

Answer using ONLY the retrieved context.

Rules:
1. Never invent facts.
2. If the context cannot answer the question, answer exactly:
   I don't know
3. Never invent prices, fares, timings or distances.
4. Cite sources used in factual answers.
5. Use only source URLs present in the retrieved context.
6. Do not invent page numbers.
7. Return valid JSON only.

Required response:
{
    "answer": "Your answer.",
    "citations": [
        {
            "title": "Destination title",
            "source_url": "Source URL"
        }
    ]
}

For an unanswerable question:
{
    "answer": "I don't know",
    "citations": []
}
"""


def load_questions():
    with open(DATASET_FILE, encoding="utf-8") as file:
        return json.load(file)


def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding="utf-8") as file:
            return json.load(file)

    return {
        "configuration_b_results": []
    }


def save_progress(progress):
    PROGRESS_FILE.write_text(
        json.dumps(progress, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


def load_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    return client.get_collection(
        name=CONFIG_B["collection_name"]
    )


def retrieve_chunks(question, collection, model):
    embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    results = collection.query(
        query_embeddings=embedding.tolist(),
        n_results=min(CONFIG_B["top_k"], collection.count()),
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]

        retrieved.append({
            "content": document,
            "title": metadata.get("title", "Unknown"),
            "district": metadata.get("district", "Unknown"),
            "category": metadata.get("category", "Unknown"),
            "source_url": metadata.get("source_url", ""),
            "cosine_distance": float(
                results["distances"][0][index]
            )
        })

    return retrieved


def generate_answer(question, chunks):
    if not chunks:
        return {"answer": "I don't know", "citations": []}

    context = json.dumps(
        chunks,
        ensure_ascii=False,
        indent=2
    )

    message = f"""
Retrieved context:
{context}

Question:
{question}

Answer only from the retrieved context.
If the answer is missing, return exactly "I don't know".
Return valid JSON only.
"""

    for attempt in range(3):
        try:
            response = generate_response(
                SYSTEM_PROMPT,
                message
            )

            response = response.strip()
            response = re.sub(r"^```(?:json)?\s*", "", response)
            response = re.sub(r"\s*```$", "", response)

            parsed = json.loads(response)

            answer = parsed.get("answer", "I don't know")
            citations = parsed.get("citations", [])

            if not isinstance(answer, str):
                return {"answer": "I don't know", "citations": []}

            valid_sources = {
                (chunk["title"], chunk["source_url"])
                for chunk in chunks
                if chunk["source_url"]
            }

            validated = []

            if isinstance(citations, list):
                for citation in citations:
                    if not isinstance(citation, dict):
                        continue

                    pair = (
                        citation.get("title"),
                        citation.get("source_url")
                    )

                    if pair in valid_sources:
                        validated.append({
                            "title": pair[0],
                            "source_url": pair[1]
                        })

            if answer.strip().lower() == "i don't know":
                return {"answer": "I don't know", "citations": []}

            if not validated:
                return {"answer": "I don't know", "citations": []}

            return {
                "answer": answer,
                "citations": validated
            }

        except Exception as error:
            if "429" in str(error) and attempt < 2:
                wait_seconds = 30 * (attempt + 1)
                print(
                    f"Groq rate limit reached. "
                    f"Retrying in {wait_seconds} seconds..."
                )
                time.sleep(wait_seconds)
                continue

            raise


def keyword_recall(keywords, chunks):
    if not keywords:
        return None

    text = " ".join(chunk["content"] for chunk in chunks).lower()

    matches = sum(
        keyword.lower() in text
        for keyword in keywords
    )

    return matches / len(keywords)


def answer_coverage(keywords, answer):
    if not keywords:
        return None

    matches = sum(
        keyword.lower() in answer.lower()
        for keyword in keywords
    )

    return matches / len(keywords)


def citation_coverage(chunks, citations):
    sources = {
        chunk["source_url"]
        for chunk in chunks
        if chunk["source_url"]
    }

    if not sources:
        return 0.0

    cited = {
        citation["source_url"]
        for citation in citations
    }

    return len(sources.intersection(cited)) / len(sources)


def evaluate_configuration_b(questions, progress):
    collection = load_collection()
    model = get_model()

    completed = {
        result["id"]
        for result in progress["configuration_b_results"]
    }

    print("\nResuming Configuration B")
    print("Chunk size:", CONFIG_B["chunk_size"])
    print("Top-k:", CONFIG_B["top_k"])
    print("Already completed:", len(completed))

    for item in questions:
        if item["id"] in completed:
            continue

        print(
            f"\nQuestion {item['id']}/{len(questions)}: "
            f"{item['question']}"
        )

        start = time.perf_counter()

        chunks = retrieve_chunks(
            item["question"],
            collection,
            model
        )

        generated = generate_answer(
            item["question"],
            chunks
        )

        elapsed = time.perf_counter() - start

        result = {
            "id": item["id"],
            "question": item["question"],
            "answerable": item["answerable"],
            "answer": generated["answer"],
            "citations": generated["citations"],
            "retrieved_chunks": chunks,
            "retrieval_keyword_recall": keyword_recall(
                item["expected_keywords"], chunks
            ),
            "answer_keyword_coverage": answer_coverage(
                item["expected_keywords"], generated["answer"]
            ),
            "citation_coverage": citation_coverage(
                chunks, generated["citations"]
            ),
            "response_time_seconds": round(elapsed, 4)
        }

        progress["configuration_b_results"].append(result)
        save_progress(progress)

        print("Answer:", generated["answer"][:180])
        print("Response time:", round(elapsed, 2), "seconds")
        print("Saved progress:", len(progress["configuration_b_results"]))

        # Small pause to reduce rate-limit pressure.
        time.sleep(5)

    print("\nConfiguration B completed!")


def average(values):
    values = [value for value in values if value is not None]
    return sum(values) / len(values) if values else 0.0


def calculate_metrics(results):
    retrieval = average([
        item["retrieval_keyword_recall"] for item in results
    ])

    answer = average([
        item["answer_keyword_coverage"] for item in results
    ])

    citation = average([
        item["citation_coverage"] for item in results
    ])

    unknown_items = [
        item for item in results if not item["answerable"]
    ]

    unknown_accuracy = average([
        1.0 if item["answer"].strip() == "I don't know" else 0.0
        for item in unknown_items
    ])

    response_time = average([
        item["response_time_seconds"] for item in results
    ])

    score = (
        0.40 * retrieval
        + 0.30 * answer
        + 0.20 * citation
        + 0.10 * unknown_accuracy
    )

    return {
        "configuration": "Configuration B",
        "chunk_size": 300,
        "top_k": 5,
        "collection_count": 21,
        "retrieval_recall": round(retrieval, 4),
        "answer_keyword_coverage": round(answer, 4),
        "citation_coverage": round(citation, 4),
        "unknown_answer_accuracy": round(unknown_accuracy, 4),
        "average_response_time_seconds": round(response_time, 4),
        "overall_score": round(score, 4)
    }


def save_final_report(results_b):
    metrics_b = calculate_metrics(results_b)
    configurations = [CONFIG_A_METRICS, metrics_b]

    winner = max(
        configurations,
        key=lambda item: item["overall_score"]
    )

    results_json = {
        "configuration_a": {
            "metrics": CONFIG_A_METRICS,
            "note": "Previously completed evaluation; aggregate metrics preserved."
        },
        "configuration_b": {
            "metrics": metrics_b,
            "question_results": results_b
        },
        "winner": winner["configuration"]
    }

    RESULTS_FILE.write_text(
        json.dumps(results_json, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    rows = [
        ("Chunk size", "chunk_size"),
        ("Top-k", "top_k"),
        ("Stored chunks", "collection_count"),
        ("Retrieval recall", "retrieval_recall"),
        ("Answer keyword coverage", "answer_keyword_coverage"),
        ("Citation coverage", "citation_coverage"),
        ("Unknown answer accuracy", "unknown_answer_accuracy"),
        ("Average response time (seconds)", "average_response_time_seconds"),
        ("Overall score", "overall_score")
    ]

    report = [
        "# WeekendYatri RAG Configuration Evaluation",
        "",
        "## Evaluation Setup",
        "",
        "- Evaluation questions: 15",
        "- Answerable questions: 14",
        "- Unanswerable questions: 1",
        "- Embedding model: all-MiniLM-L6-v2",
        "- Vector database: ChromaDB",
        "- Generation model: Groq",
        "",
        "## Configuration Comparison",
        "",
        "| Metric | Configuration A | Configuration B |",
        "|---|---:|---:|"
    ]

    for label, key in rows:
        report.append(
            f"| {label} | {CONFIG_A_METRICS[key]} | {metrics_b[key]} |"
        )

    report.extend([
        "",
        "## Winner",
        "",
        f"**{winner['configuration']}** achieved the higher weighted score "
        f"({winner['overall_score']:.4f}).",
        "",
        "## Scoring Method",
        "",
        "- Retrieval keyword recall: 40%",
        "- Answer keyword coverage: 30%",
        "- Citation coverage: 20%",
        "- Unknown answer accuracy: 10%",
        "",
        "The overall score is a project-defined evaluation metric, "
        "not a standard benchmark.",
        "",
        "## Notes",
        "",
        "- Configuration A metrics were preserved from its completed terminal evaluation.",
        "- Configuration B results were saved after each completed question.",
        "- Configuration B response times exclude previous interrupted attempts.",
        "- Lower response time is preferable.",
        ""
    ])

    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\n========== FINAL COMPARISON ==========")
    print(json.dumps(configurations, indent=4))
    print("\nWINNER:", winner["configuration"])
    print("Results:", RESULTS_FILE)
    print("Report:", REPORT_FILE)


def main():
    questions = load_questions()
    progress = load_progress()

    print("Total questions:", len(questions))

    evaluate_configuration_b(
        questions,
        progress
    )

    if len(progress["configuration_b_results"]) != len(questions):
        print("Evaluation incomplete. Run again to resume.")
        return

    save_final_report(
        progress["configuration_b_results"]
    )

    print("\nRAG evaluation completed successfully.")


if __name__ == "__main__":
    main()
