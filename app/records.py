# app/records.py
# WeekendYatri - Day 3
# Destination Data Management

from data.sample_records import places


# 1. Load all destination records

def load_records():

    return places


# 2. Search destinations by keyword

def search(records, keyword):

    keyword = keyword.lower()

    results = []

    for record in records:

        if (
            keyword in record["place"].lower()
            or keyword in record["district"].lower()
            or keyword in record["category"].lower()
        ):

            results.append(record)

    return results


# 3. Count records by a selected field

def count_by(records, field):

    counts = {}

    for record in records:

        value = record[field]

        if value in counts:
            counts[value] += 1

        else:
            counts[value] = 1

    return counts


# 4. Get a destination using its ID

def get_by_id(records, record_id):

    for record in records:

        if record["id"] == record_id:
            return record

    return None