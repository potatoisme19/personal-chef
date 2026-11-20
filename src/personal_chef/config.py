import os
from dotenv import load_dotenv

load_dotenv()


def get_chat_model():
    """Create the configured chat model; credentials are read from the environment."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("Install langchain-openai to run the agents") from exc
    kwargs = {"model": os.getenv("MODEL_NAME", "gpt-4o-mini"), "temperature": 0.2}
    if os.getenv("MODEL_API_KEY"):
        kwargs["api_key"] = os.environ["MODEL_API_KEY"]
    if os.getenv("MODEL_BASE_URL"):
        kwargs["base_url"] = os.environ["MODEL_BASE_URL"]
    return ChatOpenAI(**kwargs)
