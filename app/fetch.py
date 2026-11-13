
import requests
from pathlib import Path

# Folder to store downloaded HTML files
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Tourism source URLs
URLS = {
    "nashik_tourism": "https://nashik.gov.in/en/tourism/tourists-places/",
    "maharashtra_nashik": "https://maharashtratourism.gov.in/districts/nashik/",
    "maharashtra_ahilyanagar": "https://maharashtratourism.gov.in/districts/ahilya-nagar/",
    "bhandardara": "https://ahilyanagar.maharashtra.gov.in/en/tourist-place/bhandardara/"
}


def fetch_documents():
    for name, url in URLS.items():

        try:
            print(f"\nDownloading: {name}")

            response = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "WeekendYatri/1.0"}
            )

            response.raise_for_status()

            file_path = RAW_DIR / f"{name}.html"
            file_path.write_text(
                response.text,
                encoding="utf-8"
            )

            print(f"Saved: {file_path}")
            print(f"Status code: {response.status_code}")

        except requests.RequestException as error:
            print(f"Failed to download {name}: {error}")


if __name__ == "__main__":
    fetch_documents()
