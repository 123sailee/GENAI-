import pandas as pd
from app.records import load_records


def main():
    # Load destination records
    records = load_records()

    # Convert records into a Pandas DataFrame
    df = pd.DataFrame([record.__dict__ for record in records])

    print("\n========== DATASET OVERVIEW ==========")
    print("Dataset shape:", df.shape)
    print("Total destinations:", len(df))

    print("\n========== DESTINATIONS BY DISTRICT ==========")
    print(df["district"].value_counts())

    print("\n========== DESTINATIONS BY CATEGORY ==========")
    print(df["category"].value_counts())

    print("\n========== DESTINATIONS BY BEST SEASON ==========")
    print(df["best_season"].value_counts())

    print("\n========== THREE USEFUL FACTS ==========")

    print(
        "1. District with most destinations:",
        df["district"].value_counts().idxmax()
    )

    print(
        "2. Most popular destination category:",
        df["category"].value_counts().idxmax()
    )

    print(
        "3. Number of unique districts:",
        df["district"].nunique()
    )


if __name__ == "__main__":
    main()