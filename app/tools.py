
import csv
import math
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# MSRTC fare CSV location
FARE_CSV = BASE_DIR / "data" / "msrtc_fares.csv"


def get_bus_fare_per_km(round_trip_km):
    """
    Find the illustrative bus fare per km
    using the distance slabs in the CSV.
    """

    distance_for_slab = math.ceil(round_trip_km)

    try:
        with open(
            FARE_CSV,
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                min_km = float(row["min_km"])
                max_km = float(row["max_km"])
                fare = float(row["fare_per_km"])

                if min_km <= distance_for_slab <= max_km:
                    return fare

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Fare CSV not found: {FARE_CSV}"
        )

    raise ValueError(
        "No bus fare slab found for this distance."
    )


def weekend_trip_cost(
    round_trip_km,
    people,
    mode,
    stay_per_person=0,
    food_per_person=0,
    mileage_kmpl=None,
    fuel_price_per_litre=None
):
    """
    Estimate weekend trip cost for a group.

    Supported modes:
        own_car
        msrtc_bus

    Returns:
        Transport cost, stay cost, food cost,
        total group cost and per-person cost.
    """

    # Validate distance
    if (
        isinstance(round_trip_km, bool)
        or not isinstance(round_trip_km, (int, float))
        or not math.isfinite(round_trip_km)
        or round_trip_km <= 0
    ):
        raise ValueError(
            "Round-trip distance must be a positive number."
        )

    # Validate group size
    if (
        isinstance(people, bool)
        or not isinstance(people, int)
        or people < 1
    ):
        raise ValueError(
            "People must be a positive integer."
        )

    # Validate stay and food budgets
    for value, field_name in [
        (stay_per_person, "Stay budget"),
        (food_per_person, "Food budget")
    ]:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError(
                f"{field_name} must be a non-negative number."
            )

    # Validate travel mode
    if not isinstance(mode, str):
        raise ValueError("Mode must be a string.")

    mode = mode.strip().lower()

    if mode not in ("own_car", "msrtc_bus"):
        raise ValueError(
            "Mode must be 'own_car' or 'msrtc_bus'."
        )

    # Calculate transport cost
    if mode == "own_car":

        if (
            isinstance(mileage_kmpl, bool)
            or not isinstance(mileage_kmpl, (int, float))
            or not math.isfinite(mileage_kmpl)
            or mileage_kmpl <= 0
        ):
            raise ValueError(
                "Provide a positive car mileage."
            )

        if (
            isinstance(fuel_price_per_litre, bool)
            or not isinstance(fuel_price_per_litre, (int, float))
            or not math.isfinite(fuel_price_per_litre)
            or fuel_price_per_litre <= 0
        ):
            raise ValueError(
                "Provide a positive fuel price."
            )

        fuel_required = round_trip_km / mileage_kmpl

        transport_cost = (
            fuel_required * fuel_price_per_litre
        )

        transport_per_person = (
            transport_cost / people
        )

    else:

        fare_per_km = get_bus_fare_per_km(
            round_trip_km
        )

        transport_per_person = (
            round_trip_km * fare_per_km
        )

        transport_cost = (
            transport_per_person * people
        )

    # Calculate accommodation and food
    stay_total = stay_per_person * people
    food_total = food_per_person * people

    # Calculate final costs
    total_group_cost = (
        transport_cost
        + stay_total
        + food_total
    )

    cost_per_person = (
        total_group_cost / people
    )

    return {
        "mode": mode,
        "round_trip_km": round(round_trip_km, 2),
        "people": people,
        "transport_cost": round(transport_cost, 2),
        "stay_total": round(stay_total, 2),
        "food_total": round(food_total, 2),
        "total_group_cost": round(total_group_cost, 2),
        "cost_per_person": round(cost_per_person, 2)
    }
