
from pathlib import Path

import chromadb

from app.chunking import create_chunks
from app.vectorstore import get_model

# Project configuration
BASE_DIR = Path(__file__).resolve().parent.parent

EVAL_DB_DIR = BASE_DIR / "data" / "rag_eval_db"

CONFIGURATIONS = [
    {
        "name": "config_a_150",
        "chunk_size": 150,
        "collection_name": "weekendyatri_rag_150"
    },
    {
        "name": "config_b_300",
        "chunk_size": 300,
        "collection_name": "weekendyatri_rag_300"
    }
]


def build_collection(configuration):
    """Build a persistent ChromaDB collection for one configuration."""

    chunk_size = configuration["chunk_size"]
    collection_name = configuration["collection_name"]

    print("\nBuilding:", configuration["name"])
    print("Chunk size:", chunk_size)

    # Generate configurable chunks
    chunks, metadatas, ids = create_chunks(
        chunk_size=chunk_size
    )

    # Load existing embedding model
    model = get_model()

    # Generate embeddings
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # Create persistent evaluation database
    client = chromadb.PersistentClient(
        path=str(EVAL_DB_DIR)
    )

    # Delete only this evaluation collection if it exists.
    # The original Day 7 collection is not affected.
    existing = [
        collection.name
        for collection in client.list_collections()
    ]

    if collection_name in existing:
        client.delete_collection(collection_name)

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Store chunks and embeddings
    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings.tolist()
    )

    print("Collection created:", collection_name)
    print("Stored chunks:", collection.count())

    return collection.count()


def main():

    print("========== RAG EVALUATION STORE BUILDER ==========")

    total_configurations = len(CONFIGURATIONS)

    for index, configuration in enumerate(CONFIGURATIONS, start=1):

        print(f"\nConfiguration {index}/{total_configurations}")

        build_collection(configuration)

    print("\n========== BUILD COMPLETED ==========")
    print("Evaluation database:", EVAL_DB_DIR)
    print("Configurations built:", total_configurations)


if __name__ == "__main__":
    main()
