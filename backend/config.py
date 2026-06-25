"""Central config for the SEALION backend."""

from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env and backend/.env.local so ANTHROPIC_API_KEY is available
# before the Anthropic client is constructed (config is imported before ai.py
# builds the client). .env.local wins if both define a value.
_here = Path(__file__).parent
load_dotenv(_here / ".env")
load_dotenv(_here / ".env.local", override=True)

# The single research topic this workspace is scoped to (single-topic MVP).
TOPIC = "Mechanistic Interpretability"

# Claude model — the latest and most capable, per the project brief.
MODEL = "claude-opus-4-8"

# Cap on how much of a paper's converted markdown we send to Claude for
# relevance scoring + edge derivation. The head carries title/abstract/intro,
# which is enough for those.
MAX_PAPER_CHARS = 12000

# For grounded chat we send much more of an @-referenced paper so deep
# questions (specific numbers, sections) can be answered. Opus has plenty of
# context; this is per referenced paper.
CHAT_PAPER_CHARS = 60000

# Localhost dev origins allowed to call this API.
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
