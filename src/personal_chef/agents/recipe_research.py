from ..config import get_chat_model
from ..schemas.preferences import Preferences
from ..schemas.recipes import Recipe, RecipeCandidates
from ..tools.web_search import search_recipes


def research_recipes(query: str, preferences: Preferences | None = None, limit: int = 3) -> list[Recipe]:
    """Find source pages, then turn their evidence into structured recipe candidates."""
    prefs = preferences or Preferences()
    results = search_recipes.invoke({"query": f"{query} recipe"})
    evidence = "\n".join(f"{r.get('title', '')}: {r.get('url', '')}\n{r.get('content', '')}" for r in results)
    if not evidence:
        evidence = "No web results found. Create candidates from general cooking knowledge and leave source_url empty."
    model = get_chat_model().with_structured_output(RecipeCandidates)
    result = model.invoke([
        ("system", "Return up to the requested number of useful recipe candidates. Use supplied search evidence and URLs where possible. Respect allergies and dietary restrictions; never claim a recipe is safe for an allergy unless ingredients support it."),
        ("human", f"Request: {query}\nPreferences: {prefs.model_dump_json()}\nMaximum candidates: {limit}\nSearch evidence:\n{evidence}"),
    ])
    return result.recipes[:limit]


def recipe_research_agent(state: dict) -> dict:
    query = state.get("request", "")
    ingredients = state.get("ingredients")
    if ingredients and ingredients.ingredients:
        query += " using " + ", ".join(i.name for i in ingredients.ingredients)
    summary = state.get("memory_summary", "")
    if summary:
        query = f"Conversation context: {summary}\nCurrent request: {query}"
    return {"candidates": research_recipes(query, state.get("preferences"))}
