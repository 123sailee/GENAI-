# WeekendYatri - Day 1
# Interactive Menu

print("Welcome to WeekendYatri!")

while True:

    print("\n========== MAIN MENU ==========")
    print("1. About WeekendYatri")
    print("2. Sample Travel Questions")
    print("3. Check Season Suitability")
    print("0. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":

        print("\nWeekendYatri")
        print("Your affordable weekend getaway planner.")
        print("Explore Nashik, Ahilyanagar and Sambhajinagar.")

    elif choice == "2":

        print("\nSample Questions:")
        print("1. When can I see Umbrella Falls?")
        print("2. How far is Kalsubai from Bhandardara?")
        print("3. What can I visit in Nashik in one day?")

    elif choice == "3":

        month = input("\nEnter the month: ").lower()

        if month in ["june", "july", "august", "september"]:
            print("Great! Monsoon is suitable for waterfall trips.")

        elif month in ["october", "november", "december", "january", "february"]:
            print("Good! This period is suitable for many hill and sightseeing trips.")

        elif month in ["march", "april", "may"]:
            print("Summer! Prefer early morning trips and avoid waterfall trekking.")

        else:
            print("Invalid month. Please enter a valid month.")

    elif choice == "0":

        print("\nThank you for using WeekendYatri!")
        break

    else:

        print("Invalid choice. Please select 0, 1, 2 or 3.")