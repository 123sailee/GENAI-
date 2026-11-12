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
    clean_records,
    filter_by_category,
    filter_by_district,
    sort_by_place,
)


def main():
    records = load_records()
    clean_records(records)

    while True:
        print("\n========== WEEKENDYATRI ==========")
        print("1. View all destinations")
        print("2. Search destinations")
        print("3. Count by category")
        print("4. Find destination by ID")
        print("5. Filter by category")
        print("6. Filter by district")
        print("7. Sort destinations (A to Z)")
        print("8. Sort destinations (Z to A)")
        print("0. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            for record in records:
                print(
                    f"\nID: {record.id}"
                    f"\nPlace: {record.place}"
                    f"\nDistrict: {record.district}"
                    f"\nCategory: {record.category}"
                )

        elif choice == "2":
            keyword = input("Enter search keyword: ")
            results = search(records, keyword)

            if results:
                print("\nSearch Results:")
                for record in results:
                    print(
                        f"{record.id}. "
                        f"{record.place} - {record.district}"
                    )
            else:
                print("No matching destinations found.")

        elif choice == "3":
            counts = count_by(records, "category")

            print("\nCategory Summary:")
            for category, total in counts.items():
                print(f"{category}: {total}")



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

        elif choice == "5":
            category = input(
                "Enter category (nature/adventure/religious/heritage): "
            )

            results = filter_by_category(records, category)

            if results:
                print("\nFiltered Destinations:")
                for record in results:
                    print(f"{record.place} - {record.district}")
            else:
                print("No destinations found in this category.")

        elif choice == "6":
            district = input("Enter district: ")
            results = filter_by_district(records, district)

            if results:
                print("\nFiltered Destinations:")
                for record in results:
                    print(f"{record.place} - {record.district}")
            else:
                print("No destinations found in this district.")

        elif choice == "7":
            sorted_records = sort_by_place(records)
            print("\nDestinations Sorted A to Z:")
            for record in sorted_records:
                print(f"{record.place} - {record.district}")

        elif choice == "8":
            sorted_records = sort_by_place(records, reverse=True)
            print("\nDestinations Sorted Z to A:")
            for record in sorted_records:
                print(f"{record.place} - {record.district}")

        elif choice == "0":
            print("Thank you for using WeekendYatri!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

def sort_by_place(records, reverse=False):
    return sorted(
        records,
        key=lambda record: record.place.lower(),
        reverse=reverse
    )
