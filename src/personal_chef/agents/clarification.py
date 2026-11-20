from ..config import get_chat_model
from ..schemas.preferences import ClarificationDecision


def assess_clarification(state: dict) -> dict:
    """Ask one question only when missing information blocks a useful, safe recipe."""
    model = get_chat_model().with_structured_output(ClarificationDecision)
    ingredients = state.get("ingredients")
    ingredient_data = [item.model_dump() for item in ingredients.ingredients] if ingredients else []
    preferences = state.get("preferences")
    result = model.invoke([
        ("system", "Decide whether a recipe request cannot be answered usefully or safely without one essential detail. Do not ask about optional preferences such as cuisine, prep time, or servings; use defaults. Ask a concise question if the user says they want to cook from ingredients they have but no ingredients can be identified, or if a safety-critical restriction is ambiguous. Ask at most one question. Otherwise set needs_clarification=false."),
        ("human", f"Conversation summary: {state.get('memory_summary', '') or '(none)'}\nCurrent request: {state.get('request', '')}\nRecognized ingredients: {ingredient_data}\nPreferences: {preferences.model_dump() if preferences else {}}"),
    ])
    return {
        "clarification_needed": result.needs_clarification,
        "clarification_question": result.question,
    }


def ask_for_clarification(state: dict) -> dict:
    question = state.get("clarification_question") or "Could you share one more detail so I can suggest a suitable recipe?"
    return {"answer": f"I need one detail before I can suggest a recipe: {question}"}
