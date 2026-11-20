from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    notes: str | None = None


class IngredientList(BaseModel):
    ingredients: list[Ingredient] = Field(default_factory=list)
    source_text: str | None = None
