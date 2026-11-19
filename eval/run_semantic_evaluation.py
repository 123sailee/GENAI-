
from pathlib import Path

from app.vectorstore import semantic_search

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "eval" / "search_results.md"


# 10 evaluation questions
QUESTIONS = [
    "Find adventure destinations suitable for trekking.",
    "Suggest nature destinations in Ahilyanagar.",
    "Which destinations are suitable for winter?",
    "Find heritage attractions in Chhatrapati Sambhajinagar.",
    "Suggest destinations suitable for monsoon.",
    "Find religious destinations near Nashik.",
    "Which destinations involve trekking to a hill or fort?",
    "Suggest destinations for wildlife and nature lovers.",
    "Find destinations with historical architecture.",
    "Suggest weekend destinations around Nashik."
]


def run_evaluation():
    """Run semantic search evaluation and generate a Markdown report."""

    report = [
        "# WeekendYatri Semantic Search Evaluation",
        "",
        "## Evaluation Details",
        "",
        "- Embedding Model: all-MiniLM-L6-v2",
        "- Vector Database: ChromaDB",
        "- Similarity Metric: Cosine Distance",
        "- Number of Questions: 10",
        "- Maximum Results per Question: 5",
        "- Actual results may be fewer due to metadata filtering.",
        "",
        "## Retrieval Results",
        ""
    ]

    total_results = 0

    for number, question in enumerate(QUESTIONS, start=1):

        print(f"\nQuestion {number}/10: {question}")

        results = semantic_search(
            query=question,
            top_k=5
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        result_count = len(documents)
        total_results += result_count

        report.extend([
            f"### Q{number}. {question}",
            "",
            f"**Results returned: {result_count}**",
            "",
            "| Rank | Destination | District | Category | Cosine Distance |",
            "|---:|---|---|---|---:|"
        ])

        for rank, metadata in enumerate(metadatas, start=1):

            distance = float(distances[rank - 1])

            report.append(
                f"| {rank} "
                f"| {metadata.get('title', 'Unknown')} "
                f"| {metadata.get('district', 'Unknown')} "
                f"| {metadata.get('category', 'Unknown')} "
                f"| {distance:.4f} |"
            )

        if documents:
            report.extend([
                "",
                "**Top result document:**",
                "",
                "```text",
                documents[0],
                "```",
                ""
            ])
            print("Top result:", metadatas[0].get("title"))
        else:
            report.extend([
                "",
                "**No matching destinations found.**",
                ""
            ])
            print("No matching destinations found.")

        print("Results returned:", result_count)

    # Evaluation summary
    report.extend([
        "## Evaluation Summary",
        "",
        f"- Questions evaluated: {len(QUESTIONS)}",
        "- Maximum results per question: 5",
        f"- Total retrieval results: {total_results}",
        "",
        "## Observations",
        "",
        "- Semantic search retrieves destinations using sentence embeddings.",
        "- ChromaDB stores and retrieves destination vectors persistently.",
        "- Metadata filters improve district, category and season relevance.",
        "- Some queries may return fewer than five results when filters are applied.",
        "- Retrieval ranking depends on the embedding model and available destination metadata.",
        "- Cosine distance is used to compare semantic similarity; lower distance indicates greater similarity.",
        ""
    ])

    # Save report
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\n========== EVALUATION COMPLETE ==========")
    print("Questions evaluated:", len(QUESTIONS))
    print("Maximum results per question: 5")
    print("Total retrieval results:", total_results)
    print("Report saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    run_evaluation()
