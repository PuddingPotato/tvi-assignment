import os
from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")

@lru_cache(maxsize=2)
def get_embeddings(model: str = EMBEDDING_MODEL) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(model=model)

def collection_name_for(model: str = EMBEDDING_MODEL) -> str:
    return "kb_" + model.split("/")[-1].replace("-", "_").replace(".", "_")