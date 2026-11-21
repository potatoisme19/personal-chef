from ..config import get_chat_model


def summarize_thread(state: dict) -> dict:
    """Compress thread history after each completed recipe request."""
    recipe = state.get("recipe")
    evaluation = state.get("evaluation")
    result = state.get("answer") or "No recipe was selected."
    if recipe and not state.get("clarification_needed"):
        result = f"Selected recipe: {recipe.title}; serves {recipe.servings}."
        if evaluation:
            result += f" Suitability score: {evaluation.score}/100."
    messages = [*state.get("recent_turns", []), f"Assistant: {result}"]
    prompt = (
        "Update a compact memory for a cooking assistant. Preserve durable user preferences, allergies, "
        "dietary restrictions, disliked ingredients, serving defaults, and unresolved follow-ups. Include "
        "the latest recipe only if it matters for follow-up. Remove stale or redundant details. Return plain text "
        "under 120 words. If there is no useful history, return an empty string.\n\n"
        f"Previous memory:\n{state.get('memory_summary', '') or '(none)'}\n\n"
        "Recent conversation:\n" + "\n".join(messages[-6:])
    )
    summary = get_chat_model().invoke(prompt).content
    if not isinstance(summary, str):
        summary = str(summary)
    return {"memory_summary": summary.strip(), "recent_turns": messages[-4:]}
