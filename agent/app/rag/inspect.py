from pathlib import Path
from app.rag.loader import load_markdown_files
from app.rag.chunker import chunk_all

chunks = chunk_all(load_markdown_files(Path("../knowledge-base")))
print(f"total: {len(chunks)} chunks\n")
for c in chunks[:5]:
    print(f"--- [{c.metadata['source']}] {len(c.page_content)} chars")
    print(c.page_content[:500], "\n")