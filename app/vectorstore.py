from pathlib import Path

from app.chunking import create_chunks

# Project configuration
BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "weekendyatri_destinations"
MODEL_NAME = "all-MiniLM-L6-v2"

model = None


def get_model():
    """Load and reuse the embedding model."""
    global model

    if model is None:
        # Imported here so the server starts without loading torch
        from sentence_transformers import SentenceTransformer

        print("Loading embedding model:", MODEL_NAME)
        model = SentenceTransformer(MODEL_NAME)

    return model


def get_collection():
    """Connect to the persistent ChromaDB collection."""
    # Imported here so the server starts without loading chromadb
    import chromadb

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def store_embeddings():
    """Generate and store destination embeddings."""
    chunks, metadatas, ids = create_chunks()

    embedding_model = get_model()

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    collection = get_collection()

    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    print("\nChromaDB storage completed!")
    print("Collection:", COLLECTION_NAME)
    print("Stored destinations:", collection.count())
    print("Database location:", CHROMA_DIR)

    return collection


def extract_metadata_filters(query):
    """
    Identify district, category and season filters
    from the user's natural-language query.
    """
    query_lower = query.lower()
    conditions = []

    # District detection
    districts = {
        "chhatrapati sambhajinagar": "Chhatrapati Sambhajinagar",
        "ahilyanagar": "Ahilyanagar",
        "nashik": "Nashik"
    }

    for keyword, district_name in districts.items():
        if keyword in query_lower:
            conditions.append({
                "district": {"$eq": district_name}
            })
            break

    # Category detection
    category_keywords = {
        "adventure": [
            "adventure", "trekking", "trek",
            "hiking", "climbing"
        ],
        "nature": [
            "nature", "wildlife", "forest",
            "sanctuary", "natural"
        ],
        "religious": [
            "religious", "temple", "pilgrimage",
            "spiritual"
        ],
        "heritage": [
            "heritage", "historical",
            "architecture", "monument",
            "history"
        ]
    }

    for category, keywords in category_keywords.items():
        if any(keyword in query_lower for keyword in keywords):
            conditions.append({
                "category": {"$eq": category}
            })
            break

    # Season detection
    if "winter" in query_lower:
        conditions.append({
            "$or": [
                {"best_season": {"$eq": "winter"}},
                {"best_season": {"$eq": "monsoon and winter"}},
                {"best_season": {"$eq": "winter and monsoon"}}
            ]
        })

    elif "monsoon" in query_lower:
        conditions.append({
            "$or": [
                {"best_season": {"$eq": "monsoon"}},
                {"best_season": {"$eq": "monsoon and winter"}},
                {"best_season": {"$eq": "winter and monsoon"}}
            ]
        })

    # Combine detected filters
    if not conditions:
        return None

    if len(conditions) == 1:
        return conditions[0]

    return {
        "$and": conditions
    }


def semantic_search(query, top_k=5):
    """
    Retrieve destinations using semantic similarity
    combined with metadata filtering.
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise ValueError("top_k must be an integer.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    collection = get_collection()

    if collection.count() == 0:
        raise ValueError(
            "ChromaDB collection is empty. Run store_embeddings() first."
        )

    embedding_model = get_model()

    query_embedding = embedding_model.encode(
        [query.strip()],
        convert_to_numpy=True
    )

    metadata_filter = extract_metadata_filters(query)

    search_arguments = {
        "query_embeddings": query_embedding.tolist(),
        "n_results": min(top_k, collection.count()),
        "include": [
            "documents",
            "metadatas",
            "distances"
        ]
    }

    if metadata_filter:
        search_arguments["where"] = metadata_filter

    results = collection.query(**search_arguments)

    return results


if __name__ == "__main__":

    print("Testing metadata-filtered semantic search...")

    test_queries = [
        "adventure trekking destinations",
        "nature destinations in Ahilyanagar",
        "religious destinations near Nashik",
        "winter destinations",
        "monsoon destinations",
        "historical architecture"
    ]

    for query in test_queries:

        print(f"\nQuery: {query}")

        results = semantic_search(query, top_k=5)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        if not documents:
            print("No matching destinations found.")
            continue

        for index, metadata in enumerate(metadatas):

            print(
                f"{index + 1}. "
                f"{metadata.get('title')} | "
                f"{metadata.get('district')} | "
                f"{metadata.get('category')} | "
                f"Distance: {distances[index]:.4f}"
            )