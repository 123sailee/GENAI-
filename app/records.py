
import json
from pathlib import Path

from app.models import Record

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_records.json"


def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    records = []

    for item in data:
        record = Record(**item)
        records.append(record)

    return records


def search(records, keyword):
    keyword = keyword.lower().strip()

    results = []

    for record in records:
        if (
            keyword in record.place.lower()
            or keyword in record.district.lower()
            or keyword in record.category.lower()
        ):
            results.append(record)

    return results


def count_by(records, field):
    counts = {}

    for record in records:
        value = getattr(record, field)
        counts[value] = counts.get(value, 0) + 1

    return counts


def get_by_id(records, record_id):
    for record in records:
        if record.id == record_id:
            return record

    return None
