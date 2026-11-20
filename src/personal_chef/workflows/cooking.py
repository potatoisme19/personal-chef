from ..schemas.recipes import Recipe


def format_cooking_plan(recipe: Recipe) -> str:
    """Format a selected recipe as a readable cooking plan."""
    parts = [f"# {recipe.title}"]
    if recipe.description:
        parts += ["", recipe.description]
    parts += ["", f"Serves {recipe.servings}"]
    if recipe.prep_minutes is not None or recipe.cook_minutes is not None:
        times = []
        if recipe.prep_minutes is not None:
            times.append(f"{recipe.prep_minutes} min prep")
        if recipe.cook_minutes is not None:
            times.append(f"{recipe.cook_minutes} min cook")
        parts.append(" · ".join(times))
    parts += ["", "## Ingredients"]
    parts.extend(f"- {i.quantity if i.quantity is not None else ''} {i.unit or ''} {i.name}".strip() for i in recipe.ingredients)
    parts += ["", "## Method"]
    parts.extend(f"{idx}. {step}" for idx, step in enumerate(recipe.instructions, 1))
    if recipe.source_url:
        parts += ["", f"Source: {recipe.source_url}"]
    return "\n".join(parts)
