
from typing import TypedDict, Optional, Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from app.rag import ask_question
from app.tools import weekend_trip_cost


# ----------------------------------
# 1. Define Agent State
# ----------------------------------

class WeekendYatriState(TypedDict, total=False):

    message: str
    intent: str

    conversation_history: Annotated[
        list[dict],
        operator.add
    ]

    round_trip_km: float
    people: int
    mode: str

    stay_per_person: float
    food_per_person: float

    mileage_kmpl: Optional[float]
    fuel_price_per_litre: Optional[float]

    approved: bool
    result: dict
    status: str


# ----------------------------------
# 2. Intent Detection
# ----------------------------------

def detect_intent(state: WeekendYatriState):

    message = state["message"].lower()

    # Detect memory-related questions
    memory_keywords = [
        "previous question",
        "previous message",
        "what did i ask",
        "what was my last",
        "earlier question",
        "last question",
        "remember my question"
    ]

    if any(keyword in message for keyword in memory_keywords):
        return {"intent": "memory"}

    # Detect cost-related questions
    cost_keywords = [
        "cost",
        "budget",
        "expense",
        "calculate",
        "estimate",
        "price",
        "afford"
    ]

    if any(keyword in message for keyword in cost_keywords):
        return {"intent": "cost"}

    return {"intent": "rag"}


# ----------------------------------
# 3. Save User Message
# ----------------------------------

def remember_message(state: WeekendYatriState):

    return {
        "conversation_history": [
            {
                "role": "user",
                "content": state["message"]
            }
        ]
    }


# ----------------------------------
# 4. Memory Retrieval Node
# ----------------------------------

def memory_node(state: WeekendYatriState):

    history = state.get(
        "conversation_history", []
    )

    # Exclude the current question
    previous_messages = history[:-1]

    previous_questions = [
        item["content"]
        for item in previous_messages
        if item.get("role") == "user"
    ]

    if not previous_questions:

        answer = "I don't have a previous question in this conversation."

        previous_question = None

    else:

        previous_question = previous_questions[-1]

        answer = (
            f"Your previous question was: "
            f"{previous_question}"
        )

    return {
        "result": {
            "answer": answer,
            "previous_question": previous_question,
            "total_previous_questions": len(previous_questions)
        },
        "status": "completed"
    }


# ----------------------------------
# 5. RAG Search Node
# ----------------------------------

def rag_node(state: WeekendYatriState):

    result = ask_question(
        question=state["message"],
        top_k=5
    )

    return {
        "result": result,
        "status": "completed"
    }


# ----------------------------------
# 6. Human Approval Node
# ----------------------------------

def approval_node(state: WeekendYatriState):

    approval = interrupt({

        "type": "cost_approval",

        "message": (
            "The agent wants to calculate your "
            "weekend trip cost. Do you approve?"
        ),

        "trip_details": {
            "round_trip_km": state.get("round_trip_km"),
            "people": state.get("people"),
            "mode": state.get("mode")
        }
    })

    return {
        "approved": bool(approval)
    }


# ----------------------------------
# 7. Cost Calculator Node
# ----------------------------------

def cost_node(state: WeekendYatriState):

    result = weekend_trip_cost(

        round_trip_km=state["round_trip_km"],

        people=state["people"],

        mode=state["mode"],

        stay_per_person=state.get(
            "stay_per_person", 0
        ),

        food_per_person=state.get(
            "food_per_person", 0
        ),

        mileage_kmpl=state.get(
            "mileage_kmpl"
        ),

        fuel_price_per_litre=state.get(
            "fuel_price_per_litre"
        )
    )

    return {
        "result": result,
        "status": "completed"
    }


# ----------------------------------
# 8. Rejection Node
# ----------------------------------

def rejection_node(state: WeekendYatriState):

    return {
        "status": "rejected",

        "result": {
            "message": (
                "Trip cost calculation was not approved."
            )
        }
    }


# ----------------------------------
# 9. Conditional Routing
# ----------------------------------

def route_intent(state: WeekendYatriState):

    intent = state["intent"]

    if intent == "cost":
        return "approval"

    elif intent == "memory":
        return "memory"

    return "rag"


def route_approval(state: WeekendYatriState):

    if state.get("approved"):
        return "calculate"

    return "reject"


# ----------------------------------
# 10. Build LangGraph Workflow
# ----------------------------------

builder = StateGraph(WeekendYatriState)

builder.add_node(
    "detect_intent",
    detect_intent
)

builder.add_node(
    "remember_message",
    remember_message
)

builder.add_node(
    "memory",
    memory_node
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "approval",
    approval_node
)

builder.add_node(
    "calculate",
    cost_node
)

builder.add_node(
    "reject",
    rejection_node
)


# Workflow connections

builder.add_edge(
    START,
    "detect_intent"
)

builder.add_edge(
    "detect_intent",
    "remember_message"
)

builder.add_conditional_edges(
    "remember_message",
    route_intent,
    {
        "approval": "approval",
        "memory": "memory",
        "rag": "rag"
    }
)

builder.add_conditional_edges(
    "approval",
    route_approval,
    {
        "calculate": "calculate",
        "reject": "reject"
    }
)

builder.add_edge("memory", END)
builder.add_edge("rag", END)
builder.add_edge("calculate", END)
builder.add_edge("reject", END)


# ----------------------------------
# 11. Add Conversation Memory
# ----------------------------------

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# ----------------------------------
# 12. Run LangGraph Agent
# ----------------------------------

def run_graph_agent(
    message,
    thread_id,
    round_trip_km=None,
    people=None,
    mode=None,
    stay_per_person=0,
    food_per_person=0,
    mileage_kmpl=None,
    fuel_price_per_litre=None,
    approved=None
):

    if not message or not message.strip():
        raise ValueError("Message cannot be empty.")

    if not thread_id or not thread_id.strip():
        raise ValueError("Thread ID cannot be empty.")

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # Resume an interrupted approval request
    if approved is not None:

        result = graph.invoke(
            Command(resume=approved),
            config=config
        )

    else:

        initial_state = {
            "message": message,

            "round_trip_km": round_trip_km,
            "people": people,
            "mode": mode,

            "stay_per_person": stay_per_person,
            "food_per_person": food_per_person,

            "mileage_kmpl": mileage_kmpl,
            "fuel_price_per_litre": fuel_price_per_litre
        }

        result = graph.invoke(
            initial_state,
            config=config
        )

    # Check for pending human approval
    if "__interrupt__" in result:

        return {
            "status": "awaiting_approval",

            "interrupt": [
                item.value
                for item in result["__interrupt__"]
            ]
        }

    return {
        "status": result.get(
            "status", "completed"
        ),

        "intent": result.get("intent"),

        "result": result.get("result")
    }
