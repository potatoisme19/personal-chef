from pydantic import BaseModel, Field


class Preferences(BaseModel):
    dietary_restrictions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    cuisines: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    servings: int = Field(default=2, ge=1, le=30)
    max_prep_minutes: int | None = Field(default=None, ge=0)
    max_cook_minutes: int | None = Field(default=None, ge=0)
    extra_instructions: str | None = None


class ClarificationDecision(BaseModel):
    needs_clarification: bool = False
    question: str | None = None
