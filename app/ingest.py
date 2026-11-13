
import json
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
INPUT_FILE = BASE_DIR / "data" / "sample_records.json"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"

REQUIRED_FIELDS = [
    "place",
    "district",
    "category",
    "best_season",
    "how_to_reach",
    "source_url"
]


def extract_page_text(file_path):
    """Extract clean text from an HTML file."""
    try:
        html_content = file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_content, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True).lower()

    except (OSError, UnicodeError) as error:
        print(f"Could not read {file_path.name}: {error}")
        return ""


def extract_destination_details(file_path):
    """Extract clean details from an individual official destination page."""
    try:
        html_content = file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html_content, "html.parser")

        heading = soup.find("h1")
        category_tag = soup.find("div", class_="show-category")

        if not heading or not category_tag:
            return None

        expected_place = file_path.stem.replace("_", " ").lower()
        actual_place = heading.get_text(" ", strip=True).lower()

        if actual_place != expected_place:
            return None

        paragraphs = []

        excluded_phrases = [
            "content owned by",
            "developed and hosted by",
            "last updated:"
        ]

        for p in soup.find_all("p"):
            paragraph = p.get_text(" ", strip=True)

            if not paragraph:
                continue

            if any(
                phrase in paragraph.lower()
                for phrase in excluded_phrases
            ):
                continue

            paragraphs.append(paragraph)

        official_category = (
            category_tag.get_text(" ", strip=True)
            .replace("Category", "", 1)
            .strip()
        )

        return {
            "place": heading.get_text(" ", strip=True),
            "category": official_category,
            "description": paragraphs
        }

    except (OSError, UnicodeError) as error:
        print(f"Could not extract {file_path.name}: {error}")
        return None


def clean_record(record):
    """Validate and clean one destination record."""
    try:
        cleaned = {}

        for field in REQUIRED_FIELDS:
            value = record.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Invalid or missing field: {field}")

            cleaned[field] = value.strip()

        cleaned["id"] = record["id"]
        cleaned["verified_in_sources"] = []
        cleaned["official_details"] = {}

        return cleaned

    except (KeyError, TypeError, ValueError) as error:
        print(f"Skipping bad record: {error}")
        return None


def ingest_records():
    """Load, validate, enrich and save destination records."""

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        raw_records = json.load(file)

    source_text = {}
    destination_details = {}

    for file_path in RAW_DIR.glob("*.html"):

        text = extract_page_text(file_path)

        if text:
            source_text[file_path.name] = text

        details = extract_destination_details(file_path)

        if details:
            place_key = details["place"].strip().lower()
            destination_details[place_key] = details

    cleaned_records = []

    for raw_record in raw_records:
        try:
            record = clean_record(raw_record)

            if record is None:
                continue

            destination = record["place"].strip().lower()

            matching_sources = [
                filename
                for filename, text in source_text.items()
                if destination in text
            ]

            record["verified_in_sources"] = matching_sources

            record["official_details"] = destination_details.get(
                destination, {}
            )

            cleaned_records.append(record)

        except Exception as error:
            print(f"Unexpected error while processing record: {error}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            cleaned_records,
            file,
            ensure_ascii=False,
            indent=4
        )

    verified = sum(
        bool(record["verified_in_sources"])
        for record in cleaned_records
    )

    enriched = sum(
        bool(record["official_details"])
        for record in cleaned_records
    )

    print("\n========== INGESTION REPORT ==========")
    print("Total input records:", len(raw_records))
    print("Valid records:", len(cleaned_records))
    print("Skipped records:", len(raw_records) - len(cleaned_records))
    print("Records mentioning source pages:", verified)
    print("Records with official extracted details:", enriched)
    print("Output file:", OUTPUT_FILE)
    print("\nIngestion completed!")


if __name__ == "__main__":
    ingest_records()
