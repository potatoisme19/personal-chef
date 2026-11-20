# Personal Chef

A starter project for a LangChain-based personal cooking assistant. The scaffold is organized around focused agents, structured recipe and ingredient schemas, reusable tools, and cooking and discovery workflows.

## Project structure

- `src/personal_chef/agents/` — ingredient recognition, recipe research and adaptation, evaluation, and orchestration.
- `src/personal_chef/schemas/` — structured ingredient, preference, and recipe data models.
- `src/personal_chef/tools/` — page retrieval, quantity handling, and web search utilities.
- `src/personal_chef/workflows/` — cooking and recipe discovery flows.
- `tests/` — starter tests for schemas, scoring, and workflows.
- `notebooks/` — space for exploratory and tutorial notebooks.

This repository is an initial skeleton; implementation is still in progress.

## Setup

Use Python 3.10 or newer. Create a virtual environment, install the project dependencies as they are added, and copy `.env.example` to `.env` to configure the required service keys:

```text
TAVILY_API_KEY=your-key
MODEL_API_KEY=your-key
```

Keep `.env` local. Never commit API keys or other secrets.

## Development

The package configuration and dependency list will be filled in as the project takes shape. Tests are intended to run with `pytest` once dependencies are installed.
