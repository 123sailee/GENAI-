
from sentence_transformers import SentenceTransformer

from app.chunking import create_chunks


MODEL_NAME = "all-MiniLM-L6-v2"


def generate_embeddings():
    """Generate embeddings for all destination chunks."""

    chunks, metadatas, ids = create_chunks()

    print("Loading embedding model:", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME)

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    print("\nEmbedding generation completed!")
    print("Total embeddings:", len(embeddings))
    print("Embedding dimensions:", embeddings.shape[1])

    return chunks, metadatas, ids, embeddings


if __name__ == "__main__":

    chunks, metadatas, ids, embeddings = generate_embeddings()

    print("\nFirst embedding:")
    print(embeddings[0][:10])
