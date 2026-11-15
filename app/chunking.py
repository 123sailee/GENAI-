
from app.records import load_records


def create_chunks():
    """
    Convert destination records into text chunks
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

        metadata = {
            "title": record.place,
            "district": record.district,
            "category": record.category,
            "best_season": record.best_season,
            "source_url": record.source_url or ""
        }

        chunks.append(text)
        metadatas.append(metadata)
        ids.append(f"destination_{index + 1}")

    return chunks, metadatas, ids


if __name__ == "__main__":

    chunks, metadatas, ids = create_chunks()

    print("Total chunks:", len(chunks))
    print("\nFirst chunk:")
    print(chunks[0])
    print("\nFirst chunk metadata:")
    print(metadatas[0])
