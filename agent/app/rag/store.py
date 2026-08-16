from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.embeddings import EMBEDDING_MODEL, collection_name_for, get_embeddings


def get_store(persist_dir: Path, model: str = EMBEDDING_MODEL) -> Chroma:
    
    return Chroma(
        collection_name=collection_name_for(model),
        embedding_function=get_embeddings(model),
        persist_directory=str(persist_dir),
    )


def build_store(
    docs: list[Document],
    persist_dir: Path,
    model: str = EMBEDDING_MODEL,
    reset: bool = True,
) -> Chroma:
    
    persist_dir.mkdir(parents=True, exist_ok=True)

    store = get_store(persist_dir, model)
    if reset:
        store.delete_collection()
        store = get_store(persist_dir, model)

    store.add_documents(docs)
    return store


def count_documents(store: Chroma) -> int:
    """นับจำนวน chunk ที่อยู่ใน collection"""
    return len(store.get()["ids"])
