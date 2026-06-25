"""Pydantic models — the AI boundary and the API surface.

Every Claude response the UI or graph consumes is parsed through a model here
before use. No raw model output reaches the frontend.
"""

from pydantic import BaseModel, Field


# --- AI boundary (Claude structured output) -------------------------------

class PaperAssessment(BaseModel):
    """What Claude returns for one paper, validated before storage."""

    title: str = Field(description="The paper's title.")
    authors: str = Field(
        default="",
        description="The author list as given (e.g. 'Scholz et al.' or the "
        "full names). Empty string if not determinable.",
    )
    relevance_score: int = Field(
        ge=0, le=100,
        description="How relevant this paper is to the workspace topic, 0-100.",
    )
    overview: str = Field(
        description="A 1-2 sentence plain-language overview of the paper.",
    )
    related_titles: list[str] = Field(
        default_factory=list,
        description="Titles, chosen from the provided existing-papers list, "
        "that this paper is most topically related to.",
    )


# --- API surface ----------------------------------------------------------

class Paper(BaseModel):
    """A stored paper. `markdown` is kept server-side; not all fields are
    sent to every endpoint."""

    id: str
    title: str
    authors: str = ""
    url: str | None = None
    relevance_score: int
    overview: str
    edges: list[str] = Field(default_factory=list)  # ids of related papers
    markdown: str = ""


class PaperOut(BaseModel):
    """Paper shape sent to the left-pane library (no heavy markdown)."""

    id: str
    title: str
    authors: str = ""
    url: str | None
    relevance_score: int
    overview: str
    edges: list[str]


class GraphNode(BaseModel):
    id: str
    name: str
    relevance: int


class GraphLink(BaseModel):
    source: str
    target: str


class Graph(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]


class IngestUrlRequest(BaseModel):
    url: str


class ChatRequest(BaseModel):
    question: str
    paper_ids: list[str] = Field(default_factory=list)  # @-referenced papers


class ChatResponse(BaseModel):
    answer: str
    cited_ids: list[str]
