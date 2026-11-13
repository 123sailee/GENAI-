
from fastapi import FastAPI
from app.records import load_records

app = FastAPI(
    title="WeekendYatri API",
    description="API for discovering weekend destinations",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "WeekendYatri API is running!"
    }
@app.get("/records")
def get_records(limit: int = 20):
    records = load_records()
    return records[:limit]


from fastapi import HTTPException

@app.get("/records/{record_id}")
def get_record(record_id: int):
    records = load_records()

    for record in records:
        if record.id == record_id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Destination not found"
    )


@app.get("/search")
def search_records(q: str):
    records = load_records()
    query = q.lower().strip()

    results = [
        record for record in records
        if query in record.place.lower()
        or query in record.district.lower()
        or query in record.category.lower()
    ]

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }

