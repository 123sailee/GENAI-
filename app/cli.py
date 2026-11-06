# app/cli.py
# WeekendYatri - Day 3
# Command Line Interface

import os
import sys

if __package__ in (None, ""):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from app.records import (
    load_records,
    search,
    count_by,
    get_by_id,
)


def main():

    records = load_records()

    while True:

        print("\n========== WEEKENDYATRI ==========")
        print("1. View all destinations")
        print("2. Search destinations")
        print("3. Count by category")
        print("4. Find destination by ID")
        print("0. Exit")

        choice = input("\nEnter your choice: ")

        # Option 1: Display all destinations

        if choice == "1":

            for record in records:

                print(
                    f"\nID: {record['id']}"
                    f"\nPlace: {record['place']}"
                    f"\nDistrict: {record['district']}"
                    f"\nCategory: {record['category']}"
                )

        # Option 2: Search destinations

        elif choice == "2":

            keyword = input("Enter search keyword: ")

            results = search(records, keyword)

            if results:

                print("\nSearch Results:")

                for record in results:
                    print(
                        f"{record['id']}. "
                        f"{record['place']} - "
                        f"{record['district']}"
                    )

            else:
                print("No matching destinations found.")

        # Option 3: Count by category

        elif choice == "3":

            counts = count_by(records, "category")

            print("\nCategory Summary:")

            for category, total in counts.items():
                print(f"{category}: {total}")

        # Option 4: Find by ID

        elif choice == "4":

            try:
                record_id = int(input("Enter destination ID: "))

                result = get_by_id(records, record_id)

                if result:
                    print("\nDestination Details:")
                    print(result)

                else:
                    print("Destination ID not found.")

            except ValueError:
                print("Please enter a valid numeric ID.")

        # Option 0: Exit

        elif choice == "0":

            print("Thank you for using WeekendYatri!")
            break

        else:

            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()