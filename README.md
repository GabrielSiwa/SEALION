# SEALION

**Cursor, but for research papers.** A single-topic, AI-native research workspace.
Three panes: a relevance-sorted paper **library** (left), a **knowledge graph** /
PDF viewer (middle), and a **grounded `@`-referenced chat** (right).

See `BRIEF.md` for the locked spec and `DESIGN.md` for the visual system.

## Stack

- **Frontend** — React + Vite (JS) SPA · `react-force-graph-2d`
- **Backend** — FastAPI · `markitdown` (PDF/URL → markdown) · Anthropic SDK (Claude `claude-opus-4-8`, Pydantic-validated at the AI boundary)
- **Data** — in-memory store seeded from a committed `papers.json` (built once from a URL list)
- Runs on **localhost** (frontend :5173 ↔ backend :8000).

## Run it

### 1. Backend

```bash
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your ANTHROPIC_API_KEY into .env
uvicorn main:app --reload --port 8000
```

`GET http://localhost:8000/health` should return `{"status":"ok",...}`.

### 2. Seed the demo workspace (one time)

```bash
# put one paper URL per line in backend/seed_urls.txt, then:
cd backend && . .venv/bin/activate
python seed.py               # ingests URLs → papers.json (committed)
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173
```

## The loop (Done-When)

1. Workspace loads with a relevance-sorted paper list (left).
2. Paste a URL / upload a PDF → markitdown converts it → Claude returns a
   Pydantic-validated relevance score + overview → it slots into the sorted list.
3. The paper appears as a graph node with ≥1 AI-derived topical edge.
4. Click a node → that paper's PDF opens in the middle pane (same-origin proxy).
5. Tag papers with `@ reference`, ask a question → Claude answers grounded in
   those papers' content, citing them.
