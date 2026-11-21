import re


def _option_summary(number: int, option) -> dict:
    recipe, evaluation = option.recipe, option.evaluation
    return {
        "number": number,
        "label": f"{number}. {recipe.title}",
        "title": recipe.title,
        "description": recipe.description,
        "score": evaluation.score,
        "rationale": evaluation.rationale,
        "ingredients": [
            " ".join(str(value) for value in (item.quantity, item.unit, item.name) if value is not None)
            for item in recipe.ingredients
        ],
        "prep_minutes": recipe.prep_minutes,
        "cook_minutes": recipe.cook_minutes,
        "source_url": recipe.source_url,
    }


def auto_select_recipe(state: dict) -> dict:
    """Select the sole eligible recipe without pausing for a choice."""
    option = state["recipe_options"][0]
    return {"recipe": option.recipe, "evaluation": option.evaluation, "selection_pending": False}


def _choice_number(value, options) -> int | None:
    if hasattr(value, "choice"):
        value = value.choice
    if hasattr(value, "content"):
        value = value.content
    if isinstance(value, dict):
        if "messages" in value and value["messages"]:
            value = value["messages"][-1]
        elif "content" in value:
            value = value["content"]
        else:
            value = value.get("choice", value.get("selected", value.get("response", value.get("message", ""))))
        return _choice_number(value, options)
    if isinstance(value, list) and value:
        return _choice_number(value[-1], options)
    if isinstance(value, int):
        return value if 1 <= value <= len(options) else None
    text = str(value).strip()
    lowered = text.casefold()
    for index, option in enumerate(options, start=1):
        if lowered == option.recipe.title.casefold() or option.recipe.title.casefold() in lowered:
            return index
    match = re.search(r"\b(?:option|choice|recipe)?\s*([1-9]\d*)\b", lowered)
    if match:
        number = int(match.group(1))
        return number if 1 <= number <= len(options) else None
    for word, number in (("first", 1), ("one", 1), ("second", 2), ("two", 2), ("third", 3), ("three", 3)):
        if re.search(rf"\b{word}\b", lowered) and number <= len(options):
            return number
    return None


def _apply_choice(state: dict, value) -> dict:
    options = state.get("recipe_options", [])
    number = _choice_number(value, options)
    if number is None:
        labels = "\n".join(f"{index}. {option.recipe.title}" for index, option in enumerate(options, start=1))
        return {
            "answer": f"I couldn't match that to a recipe. Please choose a number from 1 to {len(options)} or type one of these titles:\n{labels}",
            "selection_pending": True,
        }
    option = options[number - 1]
    return {"recipe": option.recipe, "evaluation": option.evaluation, "selection_pending": False, "answer": None}


def choose_recipe_with_human(state: dict) -> dict:
    """Present the shortlist as a chat message and wait for a user reply."""
    options = state.get("recipe_options", [])
    if len(options) < 2:
        return auto_select_recipe(state) if options else {}

    lines = [
        "I found these suitable recipes. Which one would you like? Reply with a number or recipe title."
    ]
    for number, option in enumerate(options, start=1):
        recipe, evaluation = option.recipe, option.evaluation
        lines.append(f"\n{number}. **{recipe.title}** — suitability score {evaluation.score:g}/100")
        if recipe.description:
            lines.append(recipe.description)
        if evaluation.rationale:
            lines.append(f"Why it fits: {evaluation.rationale}")
        time_parts = []
        if recipe.prep_minutes is not None:
            time_parts.append(f"{recipe.prep_minutes} min prep")
        if recipe.cook_minutes is not None:
            time_parts.append(f"{recipe.cook_minutes} min cooking")
        if time_parts:
            lines.append("Time: " + ", ".join(time_parts))
        if recipe.source_url:
            lines.append(f"Source: {recipe.source_url}")

    return {"answer": "\n".join(lines), "selection_pending": True}


def resolve_recipe_choice_from_message(state: dict) -> dict:
    """Handle a numbered chat reply when the UI starts a new run instead of resuming the interrupt."""
    return _apply_choice(state, state.get("request", ""))
