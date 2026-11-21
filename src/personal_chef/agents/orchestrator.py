from ..config import get_chat_model
from langchain_core.messages import HumanMessage
from ..schemas.preferences import Preferences


def parse_request(text: str, memory_summary: str = "", current_preferences: Preferences | None = None) -> Preferences:
    """Extract dietary and practical constraints from a cooking request."""
    model = get_chat_model().with_structured_output(Preferences)
    return model.invoke([
        ("system", "Update the cooking preferences using the current request. Carry forward durable preferences from the existing preferences and conversation summary unless the current request changes them. A current explicit instruction overrides memory. Use defaults when neither provides a value. Set dietary_requirements_confirmed=true only when the user explicitly gives their allergies or dietary restrictions, or explicitly says they have none. Never treat omission as confirmation. Preserve a previously true value unless the user asks to revise those requirements."),
        ("human", f"Existing preferences: {current_preferences.model_dump_json() if current_preferences else '(none)'}\nConversation summary: {memory_summary or 'No prior conversation.'}\nCurrent request: {text}"),
    ])


def orchestrator_agent(state: dict) -> dict:
    """Parse this turn's preferences and record its text in thread history."""
    latest_user_message = next(
        (message for message in reversed(state.get("messages", [])) if isinstance(message, HumanMessage)),
        None,
    )
    if latest_user_message is None:
        raise ValueError("Send a user message in the messages input.")
    content = latest_user_message.content
    if isinstance(content, str):
        request = content
    else:
        request = "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict) and part.get("type") == "text")
    if not request.strip():
        raise ValueError("The latest user message must contain text.")
    if state.get("selection_pending") and state.get("recipe_options"):
        return {
            "request": request,
            "recent_turns": [*state.get("recent_turns", []), f"User recipe choice: {request}"],
            "answer": None,
        }
    awaiting_clarification = state.get("clarification_needed", False)
    updates = {
        "request": request,
        "recent_turns": [*state.get("recent_turns", []), f"User: {request}"],
        "answer": None,
        # Keep recognized ingredients while collecting the remaining intake details.
        "ingredients": state.get("ingredients") if awaiting_clarification else None,
        "candidates": [],
        "recipe_options": [],
        "selection_pending": False,
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
