import html
import json
import uuid
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st


# ==================================================
# 1. CONFIGURATION
# ==================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = ROOT_DIR / "data" / "records.json"
FEEDBACK_FILE = ROOT_DIR / "data" / "feedback.jsonl"

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="WeekendYatri | Weekend Travel Assistant",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 2. DATA AND SEASON LOGIC
# ==================================================

@st.cache_data
def load_destinations():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def current_season():
    month = datetime.now().month

    if month in [6, 7, 8, 9]:
        return "monsoon"

    elif month in [10, 11, 12, 1, 2]:
        return "winter"

    else:
        return "summer"


def get_season_fit(best_season):
    current = current_season()
    best = str(best_season).lower()

    if "all year" in best:
        return "🟠 OK", "amber"

    if current in best:
        return "🟢 Great now", "green"

    return "🔴 Skip this month", "red"


def category_matches(destination, selected):
    category = str(
        destination.get("category", "")
    ).lower()

    category_map = {
        "Nature": ["nature", "adventure"],
        "Religious": ["religious"],
        "Heritage": ["heritage"]
    }

    return category in category_map.get(
        selected, []
    )


def find_destination_by_name(title, destinations):
    if not title:
        return None

    title = str(title).strip().lower()

    for place in destinations:
        place_name = str(
            place.get("place", "")
        ).strip().lower()

        if place_name == title:
            return place

    return None


def extract_suggestions(chunks, destinations):
    suggestions = []
    seen = set()

    for chunk in chunks or []:
        title = chunk.get("title")

        destination = find_destination_by_name(
            title,
            destinations
        )

        if destination:
            name = destination.get("place")

            if name not in seen:
                suggestions.append(destination)
                seen.add(name)

    return suggestions


# ==================================================
# 3. FEEDBACK
# ==================================================

def save_feedback(question, answer, rating):
    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    record = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer,
        "feedback": rating
    }

    with open(
        FEEDBACK_FILE,
        "a",
        encoding="utf-8"
    ) as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


# ==================================================
# 4. API CALL
# ==================================================

def call_api(endpoint, payload):
    try:
        response = requests.post(
            f"{API_URL}{endpoint}",
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        return response.json(), None

    except requests.exceptions.RequestException as error:
        return None, str(error)


# ==================================================
# 5. DISPLAY HELPERS
# ==================================================

def display_destination(destination):
    place_name = html.escape(
        str(destination.get("place", "Unknown destination"))
    )

    district = html.escape(
        str(destination.get("district", "Unknown district"))
    )

    best_season = html.escape(
        str(destination.get("best_season", "Not specified"))
    )

    badge, badge_class = get_season_fit(
        destination.get("best_season", "")
    )

    st.markdown(
        f"""
        <div class="destination-card">
            <h4>{place_name}</h4>
            <p>📍 {district}</p>
            <p>Best season: {best_season.title()}</p>
            <span class="season-{badge_class}">
                {badge}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_destination_details(destination):
    st.write(
        destination.get(
            "how_to_reach",
            "Travel details unavailable."
        )
    )

    st.write(
        f"Category: {destination.get('category', 'Unknown').title()}"
    )

    source_url = destination.get("source_url")

    if source_url:
        st.markdown(
            f"[Official source]({source_url})"
        )


def display_citations(citations):
    if not citations:
        return

    with st.expander("📚 View source citations"):
        for idx, citation in enumerate(citations, start=1):
            title = citation.get("title", "Source")
            url = citation.get("source_url", "")

            if url:
                st.markdown(f"{idx}. [{title}]({url})")
            else:
                st.write(f"{idx}. {title}")


def display_suggestions(suggestions):
    if not suggestions:
        return

    st.markdown("### Suggested destinations")

    for destination in suggestions:
        display_destination(destination)


def format_cost_result(result):
    if not isinstance(result, dict):
        return str(result)

    if "total_group_cost" not in result:
        return result.get(
            "message",
            "The agent returned a result."
        )

    mode = result.get("mode", "unknown")

    if mode == "own_car":
        travel_mode = "Own car"
    elif mode == "msrtc_bus":
        travel_mode = "MSRTC bus"
    else:
        travel_mode = mode

    return f"""
### 💰 Trip Cost Estimate

| Item | Estimated cost |
|---|---:|
| Travel mode | {travel_mode} |
| Round-trip distance | {result.get('round_trip_km', 0)} km |
| Number of people | {result.get('people', 0)} |
| Transport | ₹{result.get('transport_cost', 0):,.2f} |
| Accommodation | ₹{result.get('stay_total', 0):,.2f} |
| Food | ₹{result.get('food_total', 0):,.2f} |
| **Total group cost** | **₹{result.get('total_group_cost', 0):,.2f}** |
| **Cost per person** | **₹{result.get('cost_per_person', 0):,.2f}** |
"""


def display_agent_result(data, destinations):
    if not isinstance(data, dict):
        st.write(data)
        return

    answer = data.get("answer")

    if answer:
        st.markdown(answer)

    elif "total_group_cost" in data:
        st.markdown(format_cost_result(data))

    elif "message" in data:
        st.info(data["message"])

    else:
        st.write(data)

    citations = data.get("citations", [])
    display_citations(citations)

    chunks = data.get("retrieved_chunks", [])
    suggestions = extract_suggestions(chunks, destinations)
    display_suggestions(suggestions)


# ==================================================
# 6. SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


# ==================================================
# 7. CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #16836b;
    margin-bottom: 0;
}

.subtitle {
    color: #8a949f;
    font-size: 1rem;
    margin-top: 0;
}

.season-green {
    background: #dcfce7;
    color: #166534;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 600;
}

.season-amber {
    background: #fef3c7;
    color: #92400e;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 600;
}

.season-red {
    background: #fee2e2;
    color: #991b1b;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 600;
}

.destination-card {
    padding: 14px;
    border: 1px solid rgba(128,128,128,0.25);
    border-radius: 12px;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 8. SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("## 🏞️ WeekendYatri")
    st.caption("Your AI-powered weekend travel companion")

    st.divider()

    # Destination category
    st.subheader("Explore by category")
    selected_category = st.selectbox(
        "Destination category",
        ["Nature", "Religious", "Heritage"]
    )
    st.caption("Adventure destinations are included under Nature.")

    st.divider()

    # AI mode
    st.subheader("Assistant settings")
    assistant_mode = st.radio(
        "Choose AI workflow",
        ["Agent (/agent)", "RAG (/ask)"]
    )

    st.divider()

    # Season
    st.markdown("### 🌦️ Current season")
    st.info(f"Current season: **{current_season().title()}**")

    st.divider()

    # Reset chat
    if st.button("🆕 New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.feedback_given = set()
        st.session_state.pending_approval = None
        st.rerun()


# ==================================================
# 9. HEADER
# ==================================================

st.markdown('<p class="main-title">WeekendYatri</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Discover affordable weekend escapes across Maharashtra.</p>',
    unsafe_allow_html=True
)

st.divider()


# ==================================================
# 10. LOAD DESTINATIONS
# ==================================================

try:
    destinations = load_destinations()
except Exception as error:
    destinations = []
    st.error(f"Could not load destinations: {error}")


# ==================================================
# 11. DESTINATION EXPLORER
# ==================================================

filtered_destinations = [
    place
    for place in destinations
    if category_matches(place, selected_category)
]

with st.expander(
    f"Explore {selected_category} destinations ({len(filtered_destinations)})",
    expanded=True
):
    if not filtered_destinations:
        st.info("No destinations found for this category.")
    else:
        columns = st.columns(2)
        for index, place in enumerate(filtered_destinations):
            with columns[index % 2]:
                display_destination(place)
                with st.popover("View details"):
                    display_destination_details(place)


st.divider()


# ==================================================
# 12. TRIP COST CALCULATOR
# ==================================================

with st.expander("💰 Estimate your weekend trip cost", expanded=False):
    st.write(
        "Fill in your trip details to request "
        "a cost estimate from the AI agent."
    )

    with st.form("trip_cost_form"):
        round_trip_km = st.number_input(
            "Round-trip distance (km)",
            min_value=1.0,
            value=100.0,
            step=10.0
        )

        people = st.number_input(
            "Number of people",
            min_value=1,
            max_value=100,
            value=2,
            step=1
        )

        mode = st.selectbox(
            "Travel mode",
            ["own_car", "msrtc_bus"],
            format_func=lambda x: (
                "Own car" if x == "own_car" else "MSRTC bus"
            )
        )

        stay_per_person = st.number_input(
            "Accommodation budget per person (₹)",
            min_value=0.0,
            value=0.0,
            step=500.0
        )

        food_per_person = st.number_input(
            "Food budget per person (₹)",
            min_value=0.0,
            value=500.0,
            step=100.0
        )

        mileage_kmpl = None
        fuel_price_per_litre = None

        if mode == "own_car":
            mileage_kmpl = st.number_input(
                "Car mileage (km/litre)",
                min_value=1.0,
                value=15.0,
                step=1.0
            )

            fuel_price_per_litre = st.number_input(
                "Fuel price (₹/litre)",
                min_value=1.0,
                value=105.0,
                step=1.0
            )

        submit_cost = st.form_submit_button(
            "Request cost estimate",
            use_container_width=True
        )

    if submit_cost:
        cost_payload = {
            "message": "Estimate the weekend trip cost.",
            "thread_id": st.session_state.thread_id,
            "round_trip_km": round_trip_km,
            "people": int(people),
            "mode": mode,
            "stay_per_person": stay_per_person,
            "food_per_person": food_per_person,
            "mileage_kmpl": mileage_kmpl,
            "fuel_price_per_litre": fuel_price_per_litre
        }

        st.session_state.pending_approval = None

        st.session_state.messages.append({
            "role": "user",
            "content": "Estimate the weekend trip cost.",
            "feedback_id": str(uuid.uuid4())
        })

        with st.spinner("WeekendYatri is preparing your cost estimate..."):
            result, error = call_api("/agent", cost_payload)

        if error:
            st.error(f"Could not calculate trip cost: {error}")
        else:
            status = result.get("status")

            if status == "awaiting_approval":
                st.session_state.pending_approval = {
                    "payload": cost_payload,
                    "interrupt": result.get("interrupt", [])
                }

                st.warning(
                    "The agent is requesting your approval "
                    "before calculating trip costs."
                )
            else:
                agent_result = result.get("result", {})

                if isinstance(agent_result, dict):
                    answer = format_cost_result(agent_result)
                else:
                    answer = str(agent_result)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "question": cost_payload["message"],
                    "citations": [],
                    "suggestions": [],
                    "feedback_id": str(uuid.uuid4())
                })

        st.rerun()


# ==================================================
# 13. PENDING HUMAN APPROVAL
# ==================================================

pending = st.session_state.pending_approval

if pending:
    st.warning("⚠️ The agent is waiting for your approval.")

    for interrupt_item in pending.get("interrupt", []):
        if isinstance(interrupt_item, dict):
            st.write(
                interrupt_item.get(
                    "message",
                    "Approve the cost calculation?"
                )
            )

            trip_details = interrupt_item.get("trip_details", {})
            if trip_details:
                st.json(trip_details)

    approval_col1, approval_col2 = st.columns(2)

    with approval_col1:
        approve_button = st.button(
            "✅ Approve calculation",
            use_container_width=True
        )

    with approval_col2:
        reject_button = st.button(
            "❌ Reject",
            use_container_width=True
        )

    if approve_button or reject_button:
        approval_value = approve_button

        resume_payload = pending["payload"].copy()
        resume_payload["approved"] = approval_value

        with st.spinner("Resuming the agent workflow..."):
            result, error = call_api("/agent", resume_payload)

        if error:
            st.error(f"Could not resume agent: {error}")
        else:
            status = result.get("status")
            agent_result = result.get("result", {})

            if status == "completed":
                answer = format_cost_result(agent_result)
            elif status == "rejected":
                answer = agent_result.get(
                    "message",
                    "Cost calculation rejected."
                )
            else:
                answer = str(agent_result)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "question": resume_payload["message"],
                "citations": [],
                "suggestions": [],
                "feedback_id": str(uuid.uuid4())
            })

            st.session_state.pending_approval = None

        st.rerun()


st.divider()


# ==================================================
# 14. CHAT INTERFACE
# ==================================================

st.subheader("💬 Ask WeekendYatri")

st.caption(
    "Ask about destinations, trekking, religious places, "
    "heritage sites and weekend travel."
)


# --------------------------------------------------
# Display previous messages
# --------------------------------------------------

for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            display_citations(message.get("citations", []))
            display_suggestions(message.get("suggestions", []))

            feedback_key = message.get("feedback_id", str(index))

            if feedback_key not in st.session_state.feedback_given:
                col1, col2 = st.columns(2)

                with col1:
                    if st.button("👍 Helpful", key=f"up_{feedback_key}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "positive"
                        )
                        st.session_state.feedback_given.add(feedback_key)
                        st.rerun()

                with col2:
                    if st.button("👎 Not helpful", key=f"down_{feedback_key}"):
                        save_feedback(
                            message.get("question", ""),
                            message["content"],
                            "negative"
                        )
                        st.session_state.feedback_given.add(feedback_key)
                        st.rerun()
            else:
                st.caption("✓ Feedback saved")


# ==================================================
# 15. PROCESS NEW CHAT QUESTION
# ==================================================

user_question = st.chat_input("Where should I travel this weekend?")

if user_question:
    st.session_state.messages.append({
        "role": "user",
        "content": user_question,
        "feedback_id": str(uuid.uuid4())
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    if assistant_mode == "Agent (/agent)":
        endpoint = "/agent"
        payload = {
            "message": user_question,
            "thread_id": st.session_state.thread_id
        }
    else:
        endpoint = "/ask"
        payload = {
            "question": user_question
        }

    cost_keywords = [
        "cost",
        "budget",
        "expense",
        "calculate",
        "estimate",
        "price",
        "afford"
    ]

    is_cost_question = any(
        keyword in user_question.lower()
        for keyword in cost_keywords
    )

    if endpoint == "/agent" and is_cost_question:
        answer = (
            "To calculate your trip budget, please use the "
            "**Trip Cost Calculator** above. Enter the distance, "
            "number of people, travel mode, and expenses. "
            "The agent will then request your approval before "
            "calculating the estimate."
        )

        citations = []
        suggestions = []

        with st.chat_message("assistant"):
            st.info(answer)

    else:
        with st.chat_message("assistant"):
            with st.spinner("WeekendYatri is planning your escape..."):
                result, error = call_api(endpoint, payload)

            citations = []
            suggestions = []

            if error:
                answer = (
                    f"Unable to connect to WeekendYatri API: {error}"
                )
                st.error(answer)

            else:
                if endpoint == "/agent":
                    status = result.get("status", "completed")
                    data = result.get("result", {})
                else:
                    status = "completed"
                    data = result

                if status == "awaiting_approval":
                    answer = (
                        "The agent is waiting for approval "
                        "before continuing."
                    )
                    st.warning(answer)

                    st.session_state.pending_approval = {
                        "payload": payload,
                        "interrupt": result.get("interrupt", [])
                    }

                elif status == "rejected":
                    answer = data.get(
                        "message",
                        "The request was rejected."
                    )
                    st.warning(answer)

                else:
                    if isinstance(data, dict):
                        answer = data.get(
                            "answer",
                            data.get(
                                "message",
                                "No answer returned."
                            )
                        )
                    else:
                        answer = str(data)

                    st.markdown(answer)

                    citations = (
                        data.get("citations", [])
                        if isinstance(data, dict)
                        else []
                    )

                    chunks = (
                        data.get("retrieved_chunks", [])
                        if isinstance(data, dict)
                        else []
                    )

                    suggestions = extract_suggestions(
                        chunks,
                        destinations
                    )

                    display_citations(citations)
                    display_suggestions(suggestions)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "question": user_question,
        "citations": citations,
        "suggestions": suggestions,
        "feedback_id": str(uuid.uuid4())
    })

    st.rerun()