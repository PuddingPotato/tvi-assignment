from pathlib import Path

def load_markdown_files(kb_dir: Path) -> list[tuple[str, str]]:

    files = sorted(kb_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No markdown files found in {kb_dir.resolve()}")

    return [(f.name, f.read_text(encoding="utf-8")) for f in files]