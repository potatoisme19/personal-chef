# Personal Chef

A LangGraph-powered personal cooking assistant that turns a natural-language cooking request into a recipe suggestion. It extracts ingredients and preferences, researches candidates, checks dietary fit, and adapts a suitable recipe. Before recipe research, the graph asks for ingredients and explicit allergy/dietary requirements when they are missing, then keeps a compact preference summary within each conversation thread.

## Project structure

- `src/personal_chef/agents/` — ingredient recognition, recipe research and adaptation, evaluation, and orchestration.
- `src/personal_chef/schemas/` — structured ingredient, preference, and recipe data models.
- `src/personal_chef/tools/` — page retrieval, quantity handling, and web search utilities.
- `src/personal_chef/workflows/` — cooking and recipe discovery flows.
- `tests/` — starter tests for schemas, scoring, and workflows.
- `notebooks/` — space for exploratory and tutorial notebooks.

The typed LangGraph flow accepts one natural-language request. It extracts
ingredients and preferences, requires ingredients and confirmed allergy/dietary
requirements, researches recipe candidates only after those are supplied,
evaluates their fit, lets the user
choose among up to three suitable options, adapts the selected recipe, and
formats the final answer. If required intake details are missing, it asks one
concise clarification question. A checkpointer stores recent turns and a short
preference summary per thread; use a new Studio thread for a separate
conversation.

## Agents and tools

| Agent or graph step | What it does | Tools and data |
| --- | --- | --- |
| Orchestrator (`orchestrator_agent`) | Reads the request and carries forward durable preferences from the current thread, while letting explicit new instructions take precedence. | Structured model output using `Preferences`. |
| Ingredient recognition (`ingredient_recognition_agent`) | Extracts only ingredients the user mentioned, with normalized names, quantities, units, and notes. | Structured model output using `IngredientList`. |
| Clarification check (`assess_clarification`) | Decides whether a missing ingredient or ambiguous safety restriction prevents a useful, safe suggestion. | Structured model output using `ClarificationDecision`; optional question is returned by `ask_for_clarification`. |
| Recipe research (`recipe_research_agent`) | Searches for recipe sources and turns the available evidence into structured candidates. | `search_recipes` (Tavily); structured `Recipe` candidates. |
| Recipe evaluation (`recipe_evaluation_agent`) | Scores candidates against the request, rejects allergy or dietary conflicts, and selects the highest scoring suitable recipe. | Structured model output using `RecipeEvaluation`. |
| Recipe choice (`choose_recipe_with_human`) | Pauses after evaluation when multiple suitable candidates remain and waits for the user's numbered choice. | LangGraph `interrupt()` with a typed `choice` field; resumes the same thread. |
| Recipe adaptation (`recipe_adaptation_agent`) | Scales quantities to the requested servings and adapts the selected recipe to the user's preferences. | `scale_quantity`; structured model output using `Recipe`. |
| Response formatter (`format_recipe_response`) | Formats the selected recipe, ingredients, method, and source as the final answer. | No external tools. |
| Thread memory (`summarize_thread`) | Compresses recent turns and the latest result into a short summary so durable preferences can carry into later requests in the same thread. | Chat model; graph checkpointer stores the thread state. |

Other reusable tools include `retrieve_page` for fetching readable page text
and `convert_temperature` for Celsius/Fahrenheit conversion. These are
available for future graph steps; the current discovery path uses web search
and quantity scaling.

### Using the graph in LangGraph Studio

Select the graph and use Chat mode. Send a normal message, for example:

> I have chicken, baked beans, and rice. Suggest dinner for four. I am allergic to peanuts and want a meal that takes under 30 minutes.

The graph accepts and returns LangChain `messages`, so the Agent UI can render
assistant replies and keep the conversation in its thread. After evaluation,
if at least two suitable recipes remain, the graph pauses with a list labelled
`1.`, `2.`, and `3.` as available. Enter a number or recipe title to resume and
receive the full recipe. The same-thread chat path also recognizes replies such
as “option 2” without rerunning recipe research.
The UI/server assigns and passes the `thread_id` in run configuration; do not
put it in the message. Continue in the same thread to retain short-term memory,
or start a new thread for a separate conversation.

You can also invoke it from Python:

```python
from personal_chef.workflows.discovery import discover_recipe

result = discover_recipe(
    "I have chicken, baked beans, and rice. Suggest dinner for four. "
    "I am allergic to peanuts and want a meal under 30 minutes."
)
print(result["messages"][-1].content)
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
`TAVILY_API_KEY` for web search and `MODEL_API_KEY` for the chat model. All
agent and memory calls use `gpt-5.4-mini`. Set `MODEL_BASE_URL` only when using a
compatible endpoint. Run the test suite with `uv run --extra dev pytest`.
