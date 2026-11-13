from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records


def search_destinations(query, top_n=5):
    records = load_records()

    if not query or not query.strip():
        return []

    # Combine destination fields into searchable text
    documents = [
        f"{record.place} {record.district} "
        f"{record.category} {record.best_season} "
        f"{record.how_to_reach}"
        for record in records
    ]

    # Convert destination text into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    destination_vectors = vectorizer.fit_transform(documents)

    # Convert the user's query into a vector
    query_vector = vectorizer.transform([query])

    # Calculate similarity scores
    scores = cosine_similarity(
        query_vector,
        destination_vectors
    ).flatten()

    # Rank destinations by similarity
    ranked_indices = scores.argsort()[::-1]

    results = []

    for index in ranked_indices:
        if scores[index] > 0:
            results.append({
                "place": records[index].place,
                "district": records[index].district,
                "category": records[index].category,
                "similarity_score": round(float(scores[index]), 3)
            })

        if len(results) == top_n:
            break

    return results


if __name__ == "__main__":
    query = input("What kind of destination are you looking for? ")

    results = search_destinations(query)

    print("\n========== SMART SEARCH RESULTS ==========")

    if results:
        for result in results:
            print(
                f"{result['place']} | "
                f"{result['district']} | "
                f"{result['category']} | "
                f"Score: {result['similarity_score']}"
            )
    else:
        print("No matching destinations found.")