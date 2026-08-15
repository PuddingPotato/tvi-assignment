import os
from functools import lru_cache

from langchain.chat_models import init_chat_model
from app.tools.fake import knowledge_search, get_leave_balance

TOOLS = [knowledge_search, get_leave_balance]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

@lru_cache(maxsize=1)
def get_model_with_tools():
    model = init_chat_model(
        model=os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"),
        model_provider=os.getenv("LLM_PROVIDER", "google_genai"),
        temperature=0,
    )
    return model.bind_tools(TOOLS)