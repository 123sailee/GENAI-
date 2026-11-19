
import json
from pathlib import Path

from app.llm import generate_response, load_system_prompt
from app.records import load_records
from app.smart_search import search_destinations

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE_DIR / "eval"

QUESTIONS_FILE = EVAL_DIR / "questions.md"
RESULTS_FILE = EVAL_DIR / "prompt_results.json"


def load_questions():
    """Extract numbered evaluation questions from Markdown."""

    questions = []

    for line in QUESTIONS_FILE.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if line and line[0].isdigit() and ". " in line:
            question = line.split(". ", 1)[1]
            questions.append(question)

    return questions


def record_to_dict(record):
    """Convert a destination record into context data."""

    return {
        "place": record.place,
        "district": record.district,
        "category": record.category,
        "best_season": record.best_season,
        "how_to_reach": record.how_to_reach,
        "source_url": record.source_url,
        "official_details": record.official_details
    }


def build_context(question):
    """
    Build context for evaluation.

    Q1 uses all Nashik destinations.
    Q3 and Q10 use complete district-wise counts.
    Other questions use TF-IDF retrieval.
    """

    records = load_records()
    query = question.lower()

    # Q1: All destinations in Nashik district
    if "destinations are available in nashik district" in query:

        district_records = [
            record for record in records
            if record.district.lower() == "nashik"
        ]

        results = [
            {
                "place": record.place,
                "district": record.district,
                "category": record.category,
                "similarity_score": 1.0
            }
            for record in district_records
        ]

        context = [
            record_to_dict(record)
            for record in district_records
        ]

        return results, context

    # Q3 and Q10: District-wise destination counts
    if (
        (
            "how many destinations" in query
            and "each district" in query
        )
        or "highest number of destinations" in query
    ):

        district_counts = {}

        for record in records:
            district = record.district

            district_counts[district] = (
                district_counts.get(district, 0) + 1
            )

        context = {
            "total_destinations": len(records),
            "district_wise_counts": district_counts
        }

        return [], context

    # Normal questions: TF-IDF retrieval
    results = search_destinations(
        question,
        top_n=5
    )

    retrieved_places = {
        item["place"] for item in results
    }

    context = [
        record_to_dict(record)
        for record in records
        if record.place in retrieved_places
    ]

    return results, context


def evaluate_prompt(version, question, context):
    """Generate and validate one prompt response."""

    system_prompt = load_system_prompt(version)

    user_message = f"""
Retrieved destination information:

{json.dumps(context, ensure_ascii=False, indent=2)}

User question:
{question}

Use only the retrieved information.
Return only the JSON format required by your system prompt.
"""

    try:
        raw_response = generate_response(
            system_prompt,
            user_message
        )

        parsed = json.loads(raw_response)

        if not isinstance(parsed, dict):
            raise ValueError(
                "Response must be a JSON object."
            )

        required_fields = (
            {"answer", "confidence", "follow_up"}
            if version == "v1"
            else {"answer", "follow_up"}
        )

        valid_fields = set(parsed.keys()) == required_fields

        valid_confidence = True

        if version == "v1":
            confidence = parsed.get("confidence")

            valid_confidence = (
                isinstance(confidence, (int, float))
                and not isinstance(confidence, bool)
                and 0 <= confidence <= 1
            )

        return {
            "response": parsed,
            "json_valid": True,
            "fields_valid": valid_fields,
            "confidence_valid": valid_confidence,
            "error": None
        }

    except Exception as error:

        return {
            "response": None,
            "json_valid": False,
            "fields_valid": False,
            "confidence_valid": False,
            "error": str(error)
        }


def main():

    questions = load_questions()

    if len(questions) != 10:
        raise ValueError(
            f"Expected 10 questions, found {len(questions)}"
        )

    results = []

    for number, question in enumerate(
        questions,
        start=1
    ):

        print(
            f"\nQuestion {number}/10: {question}"
        )

        search_results, context = build_context(question)

        if isinstance(context, list):
            context_count = len(context)
        else:
            context_count = "Complete dataset summary"

        print("Context records:", context_count)

        # Both prompts receive identical context
        v1_result = evaluate_prompt(
            "v1",
            question,
            context
        )

        v2_result = evaluate_prompt(
            "v2",
            question,
            context
        )

        question_result = {
            "question_number": number,
            "question": question,
            "retrieved_destinations": search_results,
            "context": context,
            "v1": v1_result,
            "v2": v2_result
        }

        results.append(question_result)

        print(
            "V1 JSON valid:",
            v1_result["json_valid"]
        )

        print(
            "V2 JSON valid:",
            v2_result["json_valid"]
        )

    RESULTS_FILE.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\n========== EVALUATION COMPLETE ==========")
    print("Questions evaluated:", len(results))
    print("Groq calls completed:", len(results) * 2)
    print("Results saved to:", RESULTS_FILE)


if __name__ == "__main__":
    main()
