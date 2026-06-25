"""One-time seed: ingest a list of paper URLs into a committed papers.json.

Usage:
    1. Put one paper URL per line in seed_urls.txt (blank lines / # comments ok).
    2. Ensure ANTHROPIC_API_KEY is set (e.g. in backend/.env, exported).
    3. python seed.py

Re-running rebuilds papers.json from scratch. The result is deterministic and
pays zero LLM latency at runtime — the live app just loads papers.json.
"""

from pathlib import Path

from ingest import convert_url
from pipeline import ingest_paper
import store

SEED_URLS = Path(__file__).parent / "seed_urls.txt"


def read_urls() -> list[str]:
    if not SEED_URLS.exists():
        return []
    urls = []
    for line in SEED_URLS.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def main() -> None:
    # Start from an empty store so papers.json is rebuilt fresh.
    if store.PAPERS_JSON.exists():
        store.PAPERS_JSON.unlink()
    store.load()

    urls = read_urls()
    if not urls:
        print("No URLs in seed_urls.txt — nothing to seed.")
        return

    print(f"Seeding {len(urls)} papers...\n")
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        try:
            markdown = convert_url(url)
            paper = ingest_paper(markdown, url=url)
            print(f"    -> {paper.title}  (relevance {paper.relevance_score}, "
                  f"{len(paper.edges)} edge(s))")
        except Exception as e:  # keep going; a bad URL shouldn't kill the seed
            print(f"    !! failed: {e}")

    print(f"\nDone. Wrote {store.PAPERS_JSON}")


if __name__ == "__main__":
    main()
