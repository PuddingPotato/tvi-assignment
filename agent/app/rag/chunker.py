from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]

def chunk_document(source: str, markdown_text: str) -> list[Document]:
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=True)
    chunks = splitter.split_text(markdown_text)

    out = []
    for c in chunks:
        path = " > ".join(
            v for v in (c.metadata.get("h1"), c.metadata.get("h2"), c.metadata.get("h3")) if v
        )
        out.append(Document(
            page_content=f"{path}\n\n{c.page_content}".strip(),
            metadata={**c.metadata, "source": source, "heading_path": path},
        ))
    return out


def chunk_all(files: list[tuple[str, str]]) -> list[Document]:
    return [c for source, text in files for c in chunk_document(source, text)]