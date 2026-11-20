from ..config import get_chat_model
from ..schemas.preferences import Preferences
from ..schemas.recipes import Recipe
from ..tools.quantities import scale_quantity


def adapt_recipe(recipe: Recipe, preferences: Preferences | None = None) -> Recipe:
    """Adapt a recipe to serving count and stated preferences, preserving its structure."""
    prefs = preferences or Preferences()
    scaled = recipe.model_copy(deep=True)
    if scaled.servings != prefs.servings:
        for item in scaled.ingredients:
            if item.quantity is not None:
                item.quantity = scale_quantity.invoke({
                    "quantity": item.quantity,
                    "original_servings": scaled.servings,
                    "target_servings": prefs.servings,
                })
        scaled.servings = prefs.servings
    model = get_chat_model().with_structured_output(Recipe)
    adapted = model.invoke([
        ("system", "Adapt the recipe to the preferences and serving count. Preserve the core dish, avoid all listed allergens and restrictions, and do not add ingredients that conflict with them. Keep instructions actionable."),
        ("human", f"Recipe: {scaled.model_dump_json()}\nPreferences: {prefs.model_dump_json()}"),
    ])
    adapted.servings = prefs.servings
    return adapted


def recipe_adaptation_agent(state: dict) -> dict:
    recipe = state.get("recipe")
    if recipe is None:
        return {"errors": [*state.get("errors", []), "No selected recipe to adapt"]}
    adapted = adapt_recipe(recipe, state.get("preferences"))
    return {"recipe": adapted}
