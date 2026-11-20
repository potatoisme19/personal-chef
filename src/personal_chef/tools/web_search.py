import os
from langchain_core.tools import tool


@tool
def search_recipes(query: str, max_results: int = 5) -> list[dict]:
    """Search the web for recipe pages relevant to a query."""
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
    except ImportError as exc:
        raise RuntimeError("Install langchain-community to use web search") from exc
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("TAVILY_API_KEY is required for recipe search")
    search = TavilySearchResults(max_results=max(1, min(max_results, 10)))
    return search.invoke({"query": query})


WEB_SEARCH_TOOLS = [search_recipes]
