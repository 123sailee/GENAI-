
import json
from pathlib import Path

from app.models import Record

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "records.json"


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


def validate_records(records):
    errors = []

    for record in records:

        if not record.place.strip():
            errors.append(f"Record {record.id}: Missing place name")

        if not record.district.strip():
            errors.append(f"Record {record.id}: Missing district")

        if record.category not in [
            "nature", "religious", "heritage", "adventure"
        ]:
            errors.append(f"Record {record.id}: Invalid category")

        if not record.best_season.strip():
            errors.append(f"Record {record.id}: Missing best season")

        if not record.how_to_reach.strip():
            errors.append(f"Record {record.id}: Missing travel information")

        if not record.source_url.startswith(("https://", "http://")):
            errors.append(f"Record {record.id}: Invalid source URL")

    return errors


def find_duplicates(records):
    seen = set()
    duplicates = []

    for record in records:
        place_name = record.place.lower().strip()

        if place_name in seen:
            duplicates.append(record.place)
        else:
            seen.add(place_name)

    return duplicates


def find_duplicate_ids(records):
    seen_ids = set()
    duplicates = []

    for record in records:
        if record.id in seen_ids:
            duplicates.append(record.id)
        else:
            seen_ids.add(record.id)

    return duplicates


def clean_records(records):
    validation_errors = validate_records(records)
    duplicate_places = find_duplicates(records)
    duplicate_ids = find_duplicate_ids(records)

    print("\n========== DATA CLEANING REPORT ==========")
    print("Total records:", len(records))
    print("Validation errors:", len(validation_errors))
    print("Duplicate places:", len(duplicate_places))
    print("Duplicate IDs:", len(duplicate_ids))

    if validation_errors:
        print("\nValidation Issues:")
        for error in validation_errors:
            print(error)

    print("\nData cleaning completed!")

    return records

def filter_by_category(records, category):
    category = category.lower().strip()

    return [
        record for record in records
        if record.category.lower() == category
    ]


def filter_by_district(records, district):
    district = district.lower().strip()

    return [
        record for record in records
        if record.district.lower() == district
    ]

def sort_by_place(records, reverse=False):
    return sorted(
        records,
        key=lambda record: record.place.lower(),
        reverse=reverse
    )
