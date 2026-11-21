from ..config import get_chat_model
from ..schemas.ingredients import IngredientList


def recognize_ingredients(text: str) -> IngredientList:
    """Extract normalized ingredient names, amounts, units, and notes from free text."""
    model = get_chat_model().with_structured_output(IngredientList)
    return model.invoke([
        ("system", "Extract only ingredients explicitly present. Preserve quantities and units; put uncertainty in notes. Do not invent items."),
        ("human", text),
    ])


def ingredient_recognition_agent(state: dict) -> dict:
    text = state.get("request", "")
    current = recognize_ingredients(text)
    previous_value = state.get("ingredients")

    if not state.get("clarification_needed") or not previous_value:
        return {"ingredients": current}

    previous = IngredientList.model_validate(previous_value)
    if not current.ingredients:
        return {"ingredients": previous}

    # A user may answer an intake question in separate turns, adding ingredients
    # after the first inventory was recognized. Merge by normalized ingredient name.
    merged = {item.name.strip().casefold(): item for item in previous.ingredients}
    for item in current.ingredients:
        merged[item.name.strip().casefold()] = item

    return {
        "ingredients": IngredientList(
            ingredients=list(merged.values()),
            source_text="\n".join(
                value for value in (previous.source_text, current.source_text) if value
            ) or None,
        )
    }
