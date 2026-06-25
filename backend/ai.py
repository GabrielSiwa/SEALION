"""The 10% AI layer — bounded Claude calls, Pydantic-validated at the boundary.

Two operations:
  - assess_paper: relevance score + overview + topical edges for one paper.
  - answer_question: grounded chat over @-referenced papers.
"""

import anthropic

from config import MODEL, MAX_PAPER_CHARS, TOPIC
from models import PaperAssessment

# Lazily constructed so the server (and /health) start even before the key is
# set — the client is only built when an ingest/chat call actually needs it.
_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    return _client


def assess_paper(markdown: str, existing_titles: list[str]) -> PaperAssessment:
    """Score a paper's relevance to TOPIC, summarize it, and pick which
    existing papers it relates to. Returns a Pydantic-validated assessment."""

    existing = "\n".join(f"- {t}" for t in existing_titles) or "(none yet)"
    prompt = (
        f"You are curating a research workspace on the topic: \"{TOPIC}\".\n\n"
        f"Here are the papers already in the workspace:\n{existing}\n\n"
        f"Assess this new paper (converted to markdown; may be truncated):\n\n"
        f"{markdown[:MAX_PAPER_CHARS]}\n\n"
        "Return:\n"
        "- title: the paper's actual title.\n"
        f"- relevance_score: 0-100, how relevant the paper is to \"{TOPIC}\".\n"
        "- overview: 1-2 sentences, plain language.\n"
        "- related_titles: the titles from the existing-papers list above that "
        "this paper is most topically related to (pick 0-3; use the exact "
        "strings from the list, or leave empty if none fit)."
    )

    response = get_client().messages.parse(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
        output_format=PaperAssessment,
    )
    return response.parsed_output


def answer_question(question: str, referenced: list[tuple[str, str]]) -> str:
    """Answer a question grounded in the @-referenced papers.

    `referenced` is a list of (title, markdown) tuples. The answer must cite
    the referenced papers' actual content — no hallucinated references.
    """

    if referenced:
        context = "\n\n".join(
            f"=== PAPER: {title} ===\n{md[:MAX_PAPER_CHARS]}"
            for title, md in referenced
        )
        system = (
            f"You are a research assistant for a workspace on \"{TOPIC}\". "
            "Answer ONLY from the papers provided below. Cite papers by their "
            "title in your answer. If the papers do not contain the answer, say "
            "so plainly — never invent citations or facts.\n\n" + context
        )
    else:
        system = (
            f"You are a research assistant for a workspace on \"{TOPIC}\". "
            "The user asked a question without referencing any specific paper. "
            "Answer from general knowledge and note that no paper was referenced."
        )

    response = get_client().messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    return "".join(b.text for b in response.content if b.type == "text")
