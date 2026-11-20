from typing import TypedDict
from .schemas.ingredients import IngredientList
from .schemas.preferences import Preferences
from .schemas.recipes import Recipe, RecipeEvaluation


class ChefState(TypedDict, total=False):
    request: str
    ingredients: IngredientList
    preferences: Preferences
    candidates: list[Recipe]
    recipe: Recipe | None
    evaluation: RecipeEvaluation | None
    answer: str
    errors: list[str]
    messages: list[str]
    memory_summary: str
    clarification_needed: bool
    clarification_question: str | None


class ChefInput(TypedDict):
    """The only field users need to provide in LangGraph Studio."""
    request: str


class ChefOutput(TypedDict):
    """Keep the Studio result focused on the user-facing response."""
    answer: str
