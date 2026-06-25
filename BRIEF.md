# Project Brief — Lattice (Cursor Meetup, June 2026)

> **Event slug:** 2026-06-cursor-meetup
> **Stage:** 01-ideation
> **Last updated:** 2026-06-24
> **Product name:** Lattice *(provisional — rename freely)*
>
> This file is the single source of truth for this project. Each stage appends its section before advancing. Do not re-derive what is already written here.
>
> **Project folder layout:**
> ```
> projects/2026-06-cursor-meetup/
> ├── CLAUDE.md          ← this file (project brief, created Stage 01)
> ├── repo-context.md    ← only if a repo was cloned (Stage 02 intake)
> ├── frontend/          ← React + JS (Vite) SPA (Stage 02)
> ├── backend/           ← Python + FastAPI (Stage 02)
> └── pitch/             ← deck, script, writeup (Stage 03)
> ```

---

## Event

- **Hackathon:** Cursor Meetup — June 2026 (Calgary)
- **Theme:** "Build a thing that helps with a struggle. No dashboard." (workspace ≠ dashboard — confirmed)
- **Deadline:** TBD — assumed ~24h solo sprint (same shape as SAIT)
- **Judging criteria (ranked, AI screening phase):**
  1. Innovation & Originality — 25%
  2. Technical Execution — 20% · Functional Completeness — 20% · Problem-Solution Fit — 20%
  3. UX 5% · Demo 5% · Learning 5%
- **Note:** 2-phase pipeline (AI screening → top 8 human judges). In the human round, Technical Execution rises to 25%, Problem-Solution Fit drops to 15%. Full mechanics in `shared/wiki/events/2026-05-cursor-calgary-sait.md`.

---

## Problem

Conducting a literature review means endlessly switching tools — chatting with an AI to spitball, hunting for papers, reading PDFs, taking notes, trying to remember how it all connects — with nothing holding the thread together in one place.

---

## Target User

> **Who:** A researcher / student going deep on one AI research topic (mech interp, RL, AI safety) — e.g. Jerome doing a lit review for a NeurIPS/AAAI-targeted project.
> **When:** The moment they've collected a pile of papers and are juggling a chat window, a PDF reader, and scattered notes, losing track of how the papers relate.
> **Frustration:** The AI conversation, the papers, and the connections between them all live in different windows. Nothing is grounded in *their* actual library.

---

## Wow Moment

Drop a PDF into a topic workspace and watch the AI instantly score how relevant it is, slot it into a living knowledge graph next to related papers, and then answer a grounded question about it — `@`-referencing the exact paper — without ever leaving the workspace. **"Cursor, but for research papers."**

---

## Spec
*(the contract Stage 02 builds to)*

### User Journey
*(numbered, demo order — what a judge watches in <60s)*
1. Researcher opens a workspace scoped to one topic (e.g. "mechanistic interpretability"); the **left pane** shows already-ingested papers, each with a relevance score, sorted strong→weak.
2. Researcher drops in a new PDF → markitdown converts it → Claude rates its relevance to the topic and writes a short overview; the paper appears in the left list at its sorted position.
3. The new paper appears as a **node in the middle-pane knowledge graph**, connected by AI-derived topical edges to related papers.
4. Researcher clicks a graph node → that paper's PDF opens in the middle pane.
5. In the **right-pane chat**, researcher asks a question and `@`-references one or more papers → Claude answers grounded in those papers' content, citing them.

### Done When
*(one acceptance criterion per step — "working" = this is true, live, on the deployed app)*
1. Workspace loads with a fixed topic and a non-empty, relevance-sorted paper list in the left pane.
2. Uploading a PDF returns a **Pydantic-validated** relevance score + overview from Claude and inserts the paper into the sorted left list.
3. The uploaded paper renders as a graph node with **at least one AI-derived edge** to an existing paper.
4. Clicking a graph node opens that paper's PDF in the middle pane.
5. A chat question with an `@`-referenced paper returns an answer that **cites the referenced paper's actual content** (grounded — no hallucinated references).

> **Stretch (NOT in Done When — only if core loop is shipped + deployed):** highlight a passage + leave a comment → the AI notices and incorporates the annotation into later answers. This is the strongest innovation differentiator; protect it if time allows, but never at the cost of the deployed core loop.

---

## Scope

### In scope
- Single-topic workspace (one topic, hardcoded/selected at start)
- PDF ingestion via markitdown (PDF → markdown)
- Claude relevance scoring + short overview per paper (Pydantic-validated)
- Left-pane library: list + relevance score + sort
- Middle-pane knowledge graph (node = paper, AI-derived topical edges); click node → open PDF
- Right-pane grounded chat with `@`-paper referencing
- A pre-seeded demo workspace (topic + handful of papers already ingested) for a clean live demo

### Explicitly out of scope
- Multiple topics / multi-workspace management
- Vector database / semantic search (MVP uses `@`-selected context-stuffing)
- Citation-graph scraping (edges are topical, AI-derived)
- Auth / multi-user / collaboration
- Real Zotero import/sync, browser extension, mobile
- The annotation-awareness feature (#5) is **stretch**, not in scope for the core contract

### Feasibility check
- **Buildable in time?** Yes, with the cut to one topic + markitdown + `@`-context (no vector DB) + a graph library (do not hand-roll). Risk concentrated in: two-service deploy, graph rendering, ingestion pipeline.
- **Demoable live?** Yes — the three-pane flow above is a clean sub-60s demo.
- **Does someone clearly need this?** Yes — Jerome is the named user; the judging panel (Apple ML, Google) does literature reviews.

---

## Stack

| Layer | Choice | Reason for deviation (if any) |
|---|---|---|
| Frontend | React + JavaScript (Vite SPA) | Deviation from Next.js + TS default — no SSR needed; lighter SPA. Lose compile-time types (discipline lives at the AI boundary below). |
| Backend | Python + FastAPI | Deviation from Next.js API routes — required by markitdown (Python). Mirrors Hack-the-Change 2025. |
| Ingestion | microsoft/markitdown | PDF → markdown; de-risks the data-normalization trap. |
| Data | SQLite (backend-local) or in-memory JSON | Keep minimal — single-topic demo needs no Supabase. Final call deferred to Stage 02. |
| AI / LLM | Claude (Anthropic Python SDK) | Default preferred LLM. **All structured outputs Pydantic-validated** — the Zod-equivalent that scored at Cursor Calgary. |
| Graph render | A graph lib (e.g. react-force-graph / vis-network / Cytoscape) | Do NOT hand-roll graph layout. Pick one at scaffold. |
| Deployment | Frontend → Vercel · Backend → Render or Railway | **Two targets + CORS = our #1 historical failure. "Both deployed and talking" is a Day-0 task, not an assumption.** |

## Visual Reference

**Authoritative design spec: `projects/2026-06-cursor-meetup/DESIGN.md`.** Before writing any UI code, read it — it defines tokens, typography, color, components, radii, spacing, and do's/don'ts. Do not invent colors, weights, or spacing; pull them from DESIGN.md. It is a Cursor-brand system (warm cream `#f7f7f4` canvas, Cursor Orange `#f54e00` used scarcely, CursorGothic→Inter for display/body, JetBrains Mono on every code surface, pastel AI-timeline pills). Building Lattice to look like an authentic Cursor product is intentional — it carries the "Cursor for papers" metaphor and scores brand cohesion in Pass 4.

- **Layout reference:** Jerome's mockup — a Cursor/VS Code three-pane IDE screenshot (file explorer left, document/PDF center, AI chat right). Cached at `/Users/jfran/.claude/image-cache/a6f26a80-7947-41bd-b170-5900b02a9572/1.jpeg`.
- **What to take from the mockup:** the three-pane IDE *layout*. **Left** = paper library (the file-explorer analog) with relevance scores, sortable. **Middle** = knowledge graph by default; clicking a paper opens its PDF in place (like a file opening in the editor). **Right** = AI chat with `@`-referencing.
- **Reconcile the two:** the mockup gives the *layout*; DESIGN.md gives the *visual language*. Where they conflict, DESIGN.md wins on color/type/spacing (note: DESIGN.md is light/cream editorial, not the dark IDE chrome in the screenshot — go light/cream).
- **What to ignore:** the résumé content and exact VS Code sidebar icons in the screenshot — take layout and metaphor, not that chrome.

---

## Project Skills (build-time craft)

Two project-scoped skills live in `.agents/skills/`:

- **`emil-design-eng`** — Emil Kowalski's design-engineering / animation-craft philosophy (easing curves, durations, springs, origin-awareness, perceived performance). Use while building the UI's *interaction* layer — but only **after the core loop is live and deployed**. Animation is a finishing pass, never core-loop time.
- **`review-animations`** — a manual review gate (`disable-model-invocation: true`) that audits motion code against a high craft bar. Run it **before feature freeze**, once the wow-beat interactions exist.

**Sequencing rule (non-negotiable):** working pipeline → deployed → *then* Emil polish → `review-animations` gate. If the pipeline isn't live, there is no animation budget.

**Apply craft by frequency (Emil's framework):** delight on the *rare* beats (relevance-score reveal, paper node entering the graph), standard/origin-aware on *occasional* (PDF open from node click), minimal on *frequent* (chat send). `scale(0.97)` on `:active` for every pressable. Honor `prefers-reduced-motion`.

---

## Build Notes
*(appended at Stage 02 gate)*

> Built as **SEALION** on localhost: backend :8000 (FastAPI), frontend :5173 (Vite). All 5 Done-When criteria verified end-to-end on 2026-06-24.

### Happy path
1. Backend boots, loads `papers.json` (5 mech-interp / world-model papers) into memory → `GET /papers` returns them relevance-sorted (97/95/92/88/25) → left pane renders the sorted library.
2. Paste a URL / upload a PDF → `markitdown` → Claude `messages.parse(output_format=PaperAssessment)` returns a **Pydantic-validated** relevance score + overview → paper inserts at its sorted position (live-verified: Othello-GPT paper scored 95).
3. `GET /graph` exposes nodes + AI-derived topical edges → new paper renders as a `react-force-graph-2d` node with ≥1 edge (live drop produced 3 edges).
4. Click a node (or library row) → backend **proxies the PDF same-origin** (`GET /papers/{id}/pdf`, verified `application/pdf` 3.15MB) → opens in the middle pane, sidestepping arXiv iframe blocking.
5. Tag papers `@ reference` → `POST /chat` stuffs those papers' markdown → Claude answers grounded, citing them (verified: cited the referenced paper's real findings, no hallucination).

### Key decisions made during build
- **Localhost-only** this stage (no Vercel/Render) — removed the two-service prod-deploy + CORS failure mode; Day-0 gate passed hour one.
- **Data = in-memory JSON seeded from a URL list.** `seed.py` ingests `seed_urls.txt` once → committed `papers.json`. Deterministic demo, zero runtime LLM latency on the seeded set. Live drops are **in-memory only** (`persist=False`) so every demo run starts clean.
- **Pydantic at the AI boundary** via `client.messages.parse(output_format=PaperAssessment)` — relevance score, overview, and related-titles (→ edges) all validated before reaching the UI/graph.
- **Graph lib:** `react-force-graph-2d` (force layout = the living-graph wow beat).
- **Topic** hardcoded to "Mechanistic Interpretability" in `backend/config.py` (the library leans world-models/emergent-representations — one-line change + re-seed if reframing is wanted).

### What's mocked or fragile
- **No vector DB / RAG** — chat grounding is `@`-selected context-stuffing (by design, MVP scope). Long papers are truncated to `MAX_PAPER_CHARS` (12K) at the AI boundary.
- **`@`-referencing is click-to-tag chips**, not inline `@`-autocomplete in the textbox — reliable, but the inline interaction is the natural Emil-polish upgrade.
- **Edges are backward-linking** (a new paper links to papers already in the store at ingest time); fine for the graph but not symmetric by construction.
- **Annotation-awareness (stretch #5) not built** — core loop protected first, per the sequencing rule.
- Animation is still baseline (`scale(0.97)` on press, relevance-bar reveal) — Emil polish + `review-animations` gate pending before freeze.


---

## Pitch Angle
*(appended at Stage 03 gate)*

### Hook (one sentence)


### Before / After framing


### 60-second version outline


### 3-minute version outline


---

## Coding Guidelines

**Think before coding.** State assumptions explicitly. If multiple interpretations exist, present them — don't pick silently.

**Simplicity first.** Minimum code that solves the problem. No features beyond the spec. The core loop ships and deploys before any stretch work.

**Surgical changes.** Touch only what you must. Match existing style.

**Design system is law.** Read `DESIGN.md` before any UI. Use its token references — never inline hex, never invent weights/spacing. Cursor Orange stays scarce (CTAs + wordmark only); display weight stays 400; light cream canvas, not dark.

**Validate at the AI boundary.** Every Claude response that the UI or graph consumes is parsed through a Pydantic model before use. No raw model output reaches the frontend.

**Deploy early.** Stand up both services with a `/health` check and confirm the deployed frontend reaches the deployed backend on hour one — before building features.
