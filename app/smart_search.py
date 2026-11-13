
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records


def search_destinations(query, top_n=5):
    records = load_records()

    if not query or not query.strip():
        return []

    query_lower = query.lower().strip()

    # Supported districts and destination names
    supported_locations = {
        record.district.lower()
        for record in records
    }

    supported_locations.update(
        record.place.lower()
        for record in records
    )

    # Ignore common non-location words after location prepositions
    non_location_words = {
        "winter", "summer", "monsoon", "rainy season",
        "weekend", "holidays", "adventure", "nature",
        "heritage", "religious", "budget", "trip",
        "travel", "vacation"
    }

    # Detect explicit location phrases such as:
    # "in Goa", "near Pune", "around Mumbai"
    location_match = re.search(
        r"\b(?:in|near|around|within)\s+"
        r"([a-z]+(?:\s+[a-z]+){0,2})",
        query_lower
    )

    if location_match:
        requested_location = location_match.group(1).strip()

        # Ignore phrases that refer to seasons or preferences
        if requested_location not in non_location_words:

            # Check whether the requested location is supported
            if not any(
                requested_location == location
                or requested_location in location
                for location in supported_locations
            ):
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

    # Convert user query into a vector
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity
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
                "similarity_score": round(
                    float(scores[index]), 3
                )
            })

        if len(results) == top_n:
            break

    return results


if __name__ == "__main__":
    query = input(
        "What kind of destination are you looking for? "
    )

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
