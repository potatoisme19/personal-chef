from ..config import get_chat_model
from ..schemas.preferences import Preferences
from ..schemas.recipes import EvaluatedRecipe, Recipe, RecipeEvaluation


def evaluate_recipe(recipe: Recipe, preferences: Preferences | None = None) -> RecipeEvaluation:
    """Score a recipe for preference fit, feasibility, and ingredient compatibility."""
    model = get_chat_model().with_structured_output(RecipeEvaluation)
    return model.invoke([
        ("system", "Evaluate the recipe against the user's preferences. Allergies and dietary restrictions are hard constraints: mark unsuitable and identify concerns if violated. Score from 0 to 100. Be explicit about uncertainty."),
        ("human", f"Recipe: {recipe.model_dump_json()}\nPreferences: {(preferences or Preferences()).model_dump_json()}"),
    ])


def recipe_evaluation_agent(state: dict) -> dict:
    candidates = state.get("candidates", [])
    if not candidates:
        return {"recipe_options": [], "selection_pending": False, "errors": [*state.get("errors", []), "No recipe candidates to evaluate"]}
    evaluations = [evaluate_recipe(r, state.get("preferences")) for r in candidates]
    eligible = [EvaluatedRecipe(recipe=r, evaluation=e) for r, e in zip(candidates, evaluations) if e.suitable]
    if not eligible:
        return {"recipe_options": [], "selection_pending": False, "evaluation": max(evaluations, key=lambda e: e.score), "errors": [*state.get("errors", []), "No candidate passed the suitability check"]}
    eligible.sort(key=lambda item: item.evaluation.score, reverse=True)
    options = eligible[:3]
    return {"recipe_options": options, "selection_pending": len(options) > 1}
