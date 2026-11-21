import os
from dotenv import load_dotenv

load_dotenv()


def get_chat_model():
    """Create the configured chat model; credentials are read from the environment."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError("Install langchain-openai to run the agents") from exc
    # Keep every specialist and memory call on the requested model.
    # GPT-5 uses provider-default sampling settings, so omit temperature.
    kwargs = {"model": "gpt-5.4-mini"}
    if os.getenv("MODEL_API_KEY"):
        kwargs["api_key"] = os.environ["MODEL_API_KEY"]
    if os.getenv("MODEL_BASE_URL"):
        kwargs["base_url"] = os.environ["MODEL_BASE_URL"]
    return ChatOpenAI(**kwargs)
