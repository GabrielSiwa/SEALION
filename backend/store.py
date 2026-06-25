"""In-memory paper store, seeded from papers.json on boot.

The seeded demo set is deterministic and pays zero LLM latency at runtime.
Live uploads run the full pipeline and append in memory (and to papers.json
so they survive a reload during a demo session)."""

import json
import uuid
from pathlib import Path

from models import Paper

PAPERS_JSON = Path(__file__).parent / "papers.json"

# id -> Paper
_papers: dict[str, Paper] = {}
# id -> raw PDF bytes (for uploaded files, so the PDF proxy can serve them)
_pdf_bytes: dict[str, bytes] = {}


def load() -> None:
    """Load papers.json into memory. Safe to call if the file is absent."""
    _papers.clear()
    if PAPERS_JSON.exists():
        data = json.loads(PAPERS_JSON.read_text())
        for raw in data:
            p = Paper(**raw)
            _papers[p.id] = p


def _persist() -> None:
    data = [p.model_dump() for p in _papers.values()]
    PAPERS_JSON.write_text(json.dumps(data, indent=2))


def all_sorted() -> list[Paper]:
    """Papers, strongest relevance first."""
    return sorted(_papers.values(), key=lambda p: p.relevance_score, reverse=True)


def get(paper_id: str) -> Paper | None:
    return _papers.get(paper_id)


def get_pdf_bytes(paper_id: str) -> bytes | None:
    return _pdf_bytes.get(paper_id)


def titles() -> list[str]:
    return [p.title for p in _papers.values()]


def find_id_by_title(title: str) -> str | None:
    for p in _papers.values():
        if p.title.strip().lower() == title.strip().lower():
            return p.id
    return None


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def add(paper: Paper, pdf_bytes: bytes | None = None, persist: bool = True) -> Paper:
    _papers[paper.id] = paper
    if pdf_bytes is not None:
        _pdf_bytes[paper.id] = pdf_bytes
    if persist:
        _persist()
    return paper
