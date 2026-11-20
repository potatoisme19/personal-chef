# Personal Chef

A LangGraph-powered personal cooking assistant that turns a natural-language cooking request into a recipe suggestion. It extracts ingredients and preferences, researches candidates, checks dietary fit, and adapts a suitable recipe. The graph can ask one focused clarification question and keeps a compact preference summary within each conversation thread.

## Project structure

- `src/personal_chef/agents/` — ingredient recognition, recipe research and adaptation, evaluation, and orchestration.
- `src/personal_chef/schemas/` — structured ingredient, preference, and recipe data models.
- `src/personal_chef/tools/` — page retrieval, quantity handling, and web search utilities.
- `src/personal_chef/workflows/` — cooking and recipe discovery flows.
- `tests/` — starter tests for schemas, scoring, and workflows.
- `notebooks/` — space for exploratory and tutorial notebooks.

The typed LangGraph flow accepts one natural-language request. It extracts
ingredients and preferences, checks whether a missing detail blocks a useful
answer, researches recipe candidates, evaluates their fit, adapts the best
eligible recipe, and formats a user-facing answer. If a key detail is missing,
it asks one concise clarification question. A checkpointer stores recent turns
and a short preference summary per thread; use a new Studio thread for a
separate conversation.

## Agents and tools

| Agent or graph step | What it does | Tools and data |
| --- | --- | --- |
| Orchestrator (`orchestrator_agent`) | Reads the request and carries forward durable preferences from the current thread, while letting explicit new instructions take precedence. | Structured model output using `Preferences`. |
| Ingredient recognition (`ingredient_recognition_agent`) | Extracts only ingredients the user mentioned, with normalized names, quantities, units, and notes. | Structured model output using `IngredientList`. |
| Clarification check (`assess_clarification`) | Decides whether a missing ingredient or ambiguous safety restriction prevents a useful, safe suggestion. | Structured model output using `ClarificationDecision`; optional question is returned by `ask_for_clarification`. |
| Recipe research (`recipe_research_agent`) | Searches for recipe sources and turns the available evidence into structured candidates. | `search_recipes` (Tavily); structured `Recipe` candidates. |
| Recipe evaluation (`recipe_evaluation_agent`) | Scores candidates against the request, rejects allergy or dietary conflicts, and selects the highest scoring suitable recipe. | Structured model output using `RecipeEvaluation`. |
| Recipe adaptation (`recipe_adaptation_agent`) | Scales quantities to the requested servings and adapts the selected recipe to the user's preferences. | `scale_quantity`; structured model output using `Recipe`. |
| Response formatter (`format_recipe_response`) | Formats the selected recipe, ingredients, method, and source as the final answer. | No external tools. |
| Thread memory (`summarize_thread`) | Compresses recent turns and the latest result into a short summary so durable preferences can carry into later requests in the same thread. | Chat model; graph checkpointer stores the thread state. |

Other reusable tools include `retrieve_page` for fetching readable page text
and `convert_temperature` for Celsius/Fahrenheit conversion. These are
available for future graph steps; the current discovery path uses web search
and quantity scaling.

### Example request in LangGraph Studio

The graph input has one field, `request`. In Studio, enter a prompt such as:

```json
{
  "request": "I have chicken, baked beans, and rice. Suggest dinner for four. I am allergic to peanuts and want a meal that takes under 30 minutes."
}
```

The graph returns an `answer` containing either a recipe or a clarification
question. You can also invoke it from Python:

```python
from personal_chef.workflows.discovery import discover_recipe

result = discover_recipe(
    "I have chicken, baked beans, and rice. Suggest dinner for four. "
    "I am allergic to peanuts and want a meal under 30 minutes."
)
print(result["answer"])
```

## Setup

Use Python 3.10 or newer. Install the project and development dependencies with `uv sync --extra dev`, then copy `.env.example` to `.env` and configure the service keys:

```text
TAVILY_API_KEY=your-key
MODEL_API_KEY=your-key
```

Keep `.env` local. Never commit API keys or other secrets.

## Development

Start the local LangGraph development server with `uv run langgraph dev`. The
graph is registered as `personal_chef` in `langgraph.json`. Configure
`TAVILY_API_KEY` for web search and `MODEL_API_KEY` for the chat model. Set
`MODEL_NAME` (default `gpt-4o-mini`) or `MODEL_BASE_URL` for a compatible
provider. Run the test suite with `uv run --extra dev pytest`.
