from ..config import get_chat_model
from ..schemas.preferences import ClarificationDecision


def assess_clarification(state: dict) -> dict:
    """Require ingredients and explicit dietary/allergy status before research."""
    ingredients = state.get("ingredients")
    if not ingredients or not ingredients.ingredients:
        return {
            "clarification_needed": True,
            "clarification_question": (
                "What ingredients do you have? Please also confirm any allergies or dietary "
                "restrictions (or say none). You can optionally include servings, a time limit, "
                "available equipment, or cuisine preferences."
            ),
        }

    preferences = state.get("preferences")
    if not preferences or not preferences.dietary_requirements_confirmed:
        return {
            "clarification_needed": True,
            "clarification_question": (
                "Before I search, what allergies or dietary restrictions should I account for? "
                "If you have none, please say so. You can also share servings, a time limit, "
                "available equipment, or cuisine preferences."
            ),
        }

    model = get_chat_model().with_structured_output(ClarificationDecision)
    ingredient_data = [item.model_dump() for item in ingredients.ingredients] if ingredients else []
    result = model.invoke([
        ("system", "Decide whether any recognized ingredient is ambiguous in a way that materially affects recipe suitability or safety. Do not ask about optional preferences; use defaults. Ask at most one concise question. Otherwise set needs_clarification=false."),
        ("human", f"Conversation summary: {state.get('memory_summary', '') or '(none)'}\nCurrent request: {state.get('request', '')}\nRecognized ingredients: {ingredient_data}\nPreferences: {preferences.model_dump() if preferences else {}}"),
    ])
    return {
        "clarification_needed": result.needs_clarification,
        "clarification_question": result.question,
    }


def ask_for_clarification(state: dict) -> dict:
    question = state.get("clarification_question") or "Could you share one more detail so I can suggest a suitable recipe?"
    return {"answer": f"I need one detail before I can suggest a recipe: {question}"}
