
import json
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
INPUT_FILE = BASE_DIR / "data" / "sample_records.json"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def extract_page_text(file_path):
    """Extract clean text from an HTML file."""

    html_content = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unnecessary elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    return soup.get_text(separator=" ", strip=True)


def ingest_records():
    # Load existing destination records
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    # Extract text from downloaded pages
    source_text = {}

    for file_path in RAW_DIR.glob("*.html"):
        text = extract_page_text(file_path)
        source_text[file_path.name] = text.lower()

    # Check whether each destination name appears in source pages
    for record in records:
        destination = record["place"].lower()

        matching_sources = [
            filename
            for filename, text in source_text.items()
            if destination in text
        ]

        record["verified_in_sources"] = matching_sources

    # Save cleaned structured records
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

    print("Ingestion completed!")
    print("Total records:", len(records))
    print("Output file:", OUTPUT_FILE)

    verified = sum(
        1 for record in records if record["verified_in_sources"]
    )
    print("Destinations found in downloaded pages:", verified)


if __name__ == "__main__":
    ingest_records()
