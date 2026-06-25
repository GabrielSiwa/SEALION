"""The 10% AI layer — bounded Claude calls, Pydantic-validated at the boundary.

Two operations:
  - assess_paper: relevance score + overview + topical edges for one paper.
  - answer_question: grounded chat over @-referenced papers.
"""

import anthropic

from config import MODEL, MAX_PAPER_CHARS, CHAT_PAPER_CHARS, TOPIC
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
        "- authors: the author list as printed (e.g. 'Scholz et al.' or full "
        "names); empty string if you can't tell.\n"
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


def answer_question(
    question: str,
    referenced: list[tuple[str, str]],
    catalog: list[tuple[str, str, str]],
) -> str:
    """Answer a question as a library-aware research assistant.

    `catalog` is (title, authors, overview) for every paper in the workspace —
    so the assistant can resolve a paper by title, topic, or author even when
    nothing is explicitly tagged. `referenced` is (title, markdown) for the
    papers the user @-referenced — full text provided for deep, grounded answers.
    """

    lines = []
    for title, authors, overview in catalog:
        head = f"- {title}"
        if authors:
            head += f" ({authors})"
        lines.append(f"{head} — {overview}")
    cat = "\n".join(lines) or "(the library is empty)"

    system = (
        f"You are the research assistant inside SEALION, a workspace on "
        f"\"{TOPIC}\". Be genuinely helpful and conversational.\n\n"
        f"The workspace library contains these papers "
        f"(title (authors) — overview):\n{cat}\n\n"
        "You can identify a paper the user mentions by its title, topic, or "
        "authors, and tell them about it. Use the library above plus your own "
        "knowledge to explain concepts, give background, and connect ideas.\n\n"
        "Guidelines:\n"
        "- Prioritize the workspace's papers. Name the paper(s) you draw on.\n"
        "- For specific claims, numbers, or results, ground them in a paper's "
        "provided full text (below) and don't invent figures that aren't "
        "supported. General explanation and context from your own knowledge is "
        "fine and encouraged.\n"
        "- If the user asks about a paper whose full text isn't loaded, answer "
        "from its overview and what you know, and mention they can tag it with "
        "\"@ reference\" in the library for a deeper, fully-grounded answer."
    )

    if referenced:
        full = "\n\n".join(
            f"=== FULL TEXT: {title} ===\n{md[:CHAT_PAPER_CHARS]}"
            for title, md in referenced
        )
        system += (
            "\n\nThe user has @-referenced the following paper(s); their full "
            f"text is provided for grounded answers:\n\n{full}"
        )

    response = get_client().messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": question}],
    )
    return "".join(b.text for b in response.content if b.type == "text")
