"""Central config for the SEALION backend."""

from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env so ANTHROPIC_API_KEY is available before the Anthropic
# client is constructed (config is imported before ai.py builds the client).
load_dotenv(Path(__file__).parent / ".env")

# The single research topic this workspace is scoped to (single-topic MVP).
TOPIC = "Mechanistic Interpretability"

# Claude model — the latest and most capable, per the project brief.
MODEL = "claude-opus-4-8"

# Cap on how much of a paper's converted markdown we send to Claude.
# Papers are long; the head carries title/abstract/intro, which is enough
# for relevance scoring and topical-edge derivation.
MAX_PAPER_CHARS = 12000

# Localhost dev origins allowed to call this API.
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
