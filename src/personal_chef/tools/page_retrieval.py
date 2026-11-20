from langchain_core.tools import tool


@tool
def retrieve_page(url: str) -> str:
    """Fetch a web page and return its readable text."""
    try:
        from langchain_community.document_loaders import WebBaseLoader
    except ImportError as exc:
        raise RuntimeError("Install langchain-community to retrieve web pages") from exc
    docs = WebBaseLoader(url).load()
    return "\n\n".join(doc.page_content[:12000] for doc in docs)


PAGE_TOOLS = [retrieve_page]
