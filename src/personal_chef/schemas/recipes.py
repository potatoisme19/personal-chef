from pydantic import BaseModel, Field
from .ingredients import Ingredient


class Recipe(BaseModel):
    title: str
    description: str = ""
    ingredients: list[Ingredient] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    servings: int = Field(default=2, ge=1)
    prep_minutes: int | None = None
    cook_minutes: int | None = None
    cuisine: str | None = None
    source_url: str | None = None


class RecipeEvaluation(BaseModel):
    score: float = Field(ge=0, le=100)
    rationale: str
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    suitable: bool = True


class EvaluatedRecipe(BaseModel):
    recipe: Recipe
    evaluation: RecipeEvaluation


class RecipeCandidates(BaseModel):
    recipes: list[Recipe] = Field(default_factory=list)
