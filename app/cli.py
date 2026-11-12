from app.records import (
    load_records,
    search,
    count_by,
    get_by_id,
    clean_records,
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

        elif choice == "0":
            print("Thank you for using WeekendYatri!")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
