
from app.records import load_records


def split_into_chunks(text, chunk_size=150):
    """
    Split text into word-based chunks.

    Args:
        text: Input text.
        chunk_size: Maximum number of words per chunk.

    Returns:
        List of text chunks.
    """

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")

    words = text.split()

    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk = " ".join(words[start:start + chunk_size])
        chunks.append(chunk)

    return chunks


def create_chunks(chunk_size=150):
    """
    Convert destination records into configurable text chunks
    with source and metadata information.
    """

    records = load_records()

    chunks = []
    metadatas = []
    ids = []

    for index, record in enumerate(records):

        text = f"""
Destination: {record.place}
District: {record.district}
Category: {record.category}
Best Season: {record.best_season}
How to Reach: {record.how_to_reach}
Official Details: {record.official_details}
Source: {record.source_url}
""".strip()

        text_chunks = split_into_chunks(
            text,
            chunk_size=chunk_size
        )

        for chunk_index, chunk in enumerate(text_chunks):

            metadata = {
                "title": record.place,
                "district": record.district,
                "category": record.category,
                "best_season": record.best_season,
                "source_url": record.source_url or "",
                "chunk_index": chunk_index
            }

            chunks.append(chunk)
            metadatas.append(metadata)

            ids.append(
                f"destination_{index + 1}_chunk_{chunk_index + 1}"
            )

    return chunks, metadatas, ids


if __name__ == "__main__":

    for size in [150, 300]:

        chunks, metadatas, ids = create_chunks(
            chunk_size=size
        )

        print("\nChunk size:", size)
        print("Total chunks:", len(chunks))

        if chunks:
            print("\nFirst chunk:")
            print(chunks[0])

            print("\nFirst chunk metadata:")
            print(metadatas[0])
