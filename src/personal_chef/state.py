from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from .schemas.ingredients import IngredientList
from .schemas.preferences import Preferences
from .schemas.recipes import EvaluatedRecipe, Recipe, RecipeEvaluation


class ChefState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    request: str
    ingredients: IngredientList | None
    preferences: Preferences
    candidates: list[Recipe]
    recipe_options: list[EvaluatedRecipe]
    recipe: Recipe | None
    evaluation: RecipeEvaluation | None
    answer: str | None
    errors: list[str]
    recent_turns: list[str]
    memory_summary: str
    clarification_needed: bool
    clarification_question: str | None
    selection_pending: bool


class ChefInput(TypedDict):
    """Standard LangGraph chat input; the UI supplies the current thread's messages."""
    messages: Annotated[list[AnyMessage], add_messages]


class ChefOutput(TypedDict):
    """Return chat messages so Agent UI renders the assistant response."""
    messages: Annotated[list[AnyMessage], add_messages]
