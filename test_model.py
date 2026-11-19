import json
import pathlib
from dataclasses import asdict

from app.models import Record

DATA_FILE = pathlib.Path(__file__).resolve().parent / "data" / "sample_records.json"

with open(DATA_FILE, encoding="utf-8") as file:
    places = json.load(file)

# Convert the first dictionary into a Record object
destination = Record(**places[0])

# Display the object
print("Dataclass Object:")
print(destination)

print("\nDestination Name:")
print(destination.place)

print("\nDistrict:")
print(destination.district)

# Convert object back into a dictionary
print("\nDictionary:")
print(asdict(destination))