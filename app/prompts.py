from app.retriever import Chunk
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> tuple[str, int]:
    """Prompt text and version from prompts/<name>.md (front matter, then the exact text)."""
    raw = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
    _, meta, body = raw.split("---\n", 2)
    version = int(next(line.split(":", 1)[1] for line in meta.splitlines() if line.startswith("version:")))
    return body, version


SYSTEM_PROMPT, SYSTEM_PROMPT_VERSION = _load_prompt("system_prompt")



def build_context(chunks: list[Chunk], max_chars: int) -> str:
    parts: list[str] = []
    used = 0
    for c in chunks:
        block = f"[doc:{c.doc_id}] {c.heading}\n{c.text}"
        if used + len(block) > max_chars:
            break
        parts.append(block)
        used += len(block)
    return "\n\n".join(parts)


def build_messages(question: str, chunks: list[Chunk], max_chars: int) -> list[dict[str, str]]:
    context = build_context(chunks, max_chars)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
    ]
