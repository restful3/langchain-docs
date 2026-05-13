from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv(find_dotenv())


def build_model():
    """Create the chat model used by all week2 demos."""
    model_name = os.environ.get("DEEPAGENT_MODEL", "gpt-4o-mini")
    base_url = os.environ.get("OPENAI_BASE_URL")
    extra = {"base_url": base_url} if base_url else {}
    return init_chat_model(f"openai:{model_name}", **extra)
