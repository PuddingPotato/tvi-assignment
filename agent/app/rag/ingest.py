from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

from app.rag.loader import load_markdown_files
from app.rag.chunker import chunk_all
from app.rag.store import build_store, count_documents

KB_DIR = Path("../knowledge-base")
CHROMA_DIR = Path("./chroma_db")

def run_ingest():
    files = load_markdown_files(KB_DIR)
    chunks = chunk_all(files)
    print(f"chunked {len(chunks)} chunks from {len(files)} files")
    store = build_store(chunks, CHROMA_DIR)
    print(f"Indexed {count_documents(store)} documents into {CHROMA_DIR}")


if __name__ == "__main__":
    run_ingest()