from ..config import get_chat_model
from ..schemas.preferences import Preferences


def parse_request(text: str, memory_summary: str = "", current_preferences: Preferences | None = None) -> Preferences:
    """Extract dietary and practical constraints from a cooking request."""
    model = get_chat_model().with_structured_output(Preferences)
    return model.invoke([
        ("system", "Update the cooking preferences using the current request. Carry forward durable preferences from the existing preferences and conversation summary unless the current request changes them. A current explicit instruction overrides memory. Use defaults when neither provides a value."),
        ("human", f"Existing preferences: {current_preferences.model_dump_json() if current_preferences else '(none)'}\nConversation summary: {memory_summary or 'No prior conversation.'}\nCurrent request: {text}"),
    ])


def orchestrator_agent(state: dict) -> dict:
    """Parse this turn's preferences and record its text in thread history."""
    request = state.get("request", "")
    updates = {
        "messages": [*state.get("messages", []), f"User: {request}"],
        "ingredients": None,
        "candidates": [],
        "recipe": None,
        "evaluation": None,
        "errors": [],
    }
    updates["preferences"] = parse_request(
        request,
        state.get("memory_summary", ""),
        state.get("preferences"),
    )
    return updates
