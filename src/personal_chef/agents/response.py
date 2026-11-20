def format_recipe_response(state: dict) -> dict:
    """Produce the compact user-facing answer returned by the graph."""
    recipe = state.get("recipe")
    if recipe is None:
        return {"answer": "I couldn't find a suitable recipe for that request. Try adding more detail about what you'd like to cook."}
    lines = [recipe.title]
    if recipe.description:
        lines += ["", recipe.description]
    lines += ["", f"Serves {recipe.servings}", "", "Ingredients:"]
    for ingredient in recipe.ingredients:
        amount = " ".join(str(value) for value in (ingredient.quantity, ingredient.unit) if value is not None)
        lines.append(f"- {amount} {ingredient.name}".strip())
    lines += ["", "Method:"]
    lines.extend(f"{number}. {step}" for number, step in enumerate(recipe.instructions, start=1))
    if recipe.source_url:
        lines += ["", f"Source: {recipe.source_url}"]
    return {"answer": "\n".join(lines)}
