from pathlib import Path
from functools import lru_cache
from langchain_core.documents import Document
from app.rag.store import get_store

CHROMA_DIR = Path("./chroma_db")

@lru_cache(maxsize=1)
def _store():
    return get_store(CHROMA_DIR)

def search(query: str, k: int = 4) -> list[Document]:
    return _store().similarity_search(query, k=k)