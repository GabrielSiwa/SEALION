"""The ingestion pipeline shared by the seed script and live uploads:

    source -> markdown (ingest) -> Claude assessment (Pydantic) -> edges -> store
"""

from ai import assess_paper
from models import Paper
import store


def ingest_paper(markdown: str, url: str | None = None,
                 pdf_bytes: bytes | None = None, persist: bool = True) -> Paper:
    """Assess `markdown` against the current store, derive topical edges to
    existing papers, store it, and return the new Paper."""

    existing_titles = store.titles()
    assessment = assess_paper(markdown, existing_titles)

    edges: list[str] = []
    for title in assessment.related_titles:
        related_id = store.find_id_by_title(title)
        if related_id:
            edges.append(related_id)

    paper = Paper(
        id=store.new_id(),
        title=assessment.title,
        url=url,
        relevance_score=assessment.relevance_score,
        overview=assessment.overview,
        edges=edges,
        markdown=markdown,
    )
    store.add(paper, pdf_bytes=pdf_bytes, persist=persist)
    return paper
