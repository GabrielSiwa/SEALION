# AGENTS.md — SEALION

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions below.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## Project: SEALION — "Cursor, but for research papers"

A single-topic AI-native research workspace. Three panes: **left** = paper library (relevance-sorted), **middle** = knowledge graph / PDF viewer, **right** = grounded `@`-referenced chat.

- **The spec is law:** `BRIEF.md` holds the locked Done-When contract. Build to it; don't expand scope.
- **The design is law:** `DESIGN.md` defines tokens, type, color, spacing. Read it before any UI. Never inline hex, never invent weights/spacing. Cursor Orange (`#f54e00`) stays scarce (CTAs + wordmark only). Display weight stays 400. Light cream canvas (`#f7f7f4`), not dark.
- **Validate at the AI boundary:** every Claude response the UI/graph consumes is parsed through a **Pydantic** model before use. No raw model output reaches the frontend.
- **Stack:** Vite React (JS) frontend · FastAPI backend · `markitdown` (PDF/URL → markdown) · Anthropic Python SDK (Claude) · `react-force-graph-2d` · in-memory JSON store seeded from `papers.json`.
- **Localhost-only this stage:** frontend :5173, backend :8000, CORS scoped to localhost. No cloud deploy yet.

### Animation sequencing (non-negotiable)

Working pipeline → running locally end-to-end → *then* `emil-design-eng` polish → `review-animations` gate before feature freeze. If the pipeline isn't live, there is no animation budget. Delight on rare beats (relevance reveal, node entering graph); minimal on frequent (chat send). `scale(0.97)` on `:active`; honor `prefers-reduced-motion`.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
