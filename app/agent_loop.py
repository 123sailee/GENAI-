
from app.rag import ask_question
from app.tools import weekend_trip_cost


def run_agent(
    message,
    round_trip_km=None,
    people=None,
    mode=None,
    stay_per_person=0,
    food_per_person=0,
    mileage_kmpl=None,
    fuel_price_per_litre=None
):
    """
    Handwritten WeekendYatri agent.

    Available tools:
    1. RAG destination search
    2. Weekend trip cost calculator
    """

    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    query = message.lower()

    # Detect cost-related requests
    cost_keywords = [
        "cost",
        "budget",
        "expense",
        "expenses",
        "calculate",
        "estimate",
        "price",
        "afford"
    ]

    wants_cost = any(
        keyword in query
        for keyword in cost_keywords
    )

    # Detect destination-related requests
    destination_keywords = [
        "destination",
        "place",
        "places",
        "travel",
        "trip",
        "visit",
        "suggest",
        "recommend",
        "tourist",
        "attraction"
    ]

    wants_destination = any(
        keyword in query
        for keyword in destination_keywords
    )

    # Tool 1: Cost calculator
    if wants_cost:

        required_values = [
            round_trip_km,
            people,
            mode
        ]

        if any(value is None for value in required_values):
            return {
                "agent": "WeekendYatri",
                "tool_used": "weekend_trip_cost",
                "status": "missing_information",
                "message": (
                    "Please provide round-trip distance, "
                    "number of people and travel mode."
                )
            }

        cost_result = weekend_trip_cost(
            round_trip_km=round_trip_km,
            people=people,
            mode=mode,
            stay_per_person=stay_per_person,
            food_per_person=food_per_person,
            mileage_kmpl=mileage_kmpl,
            fuel_price_per_litre=fuel_price_per_litre
        )

        return {
            "agent": "WeekendYatri",
            "tool_used": "weekend_trip_cost",
            "status": "success",
            "message": "Trip cost estimated successfully.",
            "result": cost_result
        }

    # Tool 2: RAG destination search
    if wants_destination:

        rag_result = ask_question(
            question=message,
            top_k=5
        )

        return {
            "agent": "WeekendYatri",
            "tool_used": "rag_search",
            "status": "success",
            "message": rag_result["answer"],
            "citations": rag_result["citations"]
        }

    # If intent is unclear
    return {
        "agent": "WeekendYatri",
        "tool_used": None,
        "status": "needs_clarification",
        "message": (
            "I can help you discover destinations "
            "or estimate your weekend trip cost."
        )
    }


if __name__ == "__main__":

    print("\n--- WeekendYatri Agent ---")

    # Test 1: Destination search
    print("\nTEST 1: Destination search")

    result = run_agent(
        message="Suggest adventure destinations for a weekend trip."
    )

    print(result)

    # Test 2: Cost calculation
    print("\nTEST 2: Trip cost calculation")

    result = run_agent(
        message="Calculate my weekend trip cost.",
        round_trip_km=200,
        people=4,
        mode="own_car",
        stay_per_person=800,
        food_per_person=500,
        mileage_kmpl=15,
        fuel_price_per_litre=105
    )

    print(result)
