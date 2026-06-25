"""SEALION backend — FastAPI service for the three-pane research workspace.

Routes map 1:1 to the Done-When contract:
  GET  /health                 -> liveness for the Day-0 deploy gate
  GET  /papers                 -> relevance-sorted library (left pane)
  GET  /graph                  -> nodes + AI-derived edges (middle pane graph)
  POST /papers/ingest-url      -> ingest a paper by URL (drop / paste)
  POST /papers/upload          -> ingest an uploaded PDF
  GET  /papers/{id}/pdf        -> same-origin PDF proxy (middle pane viewer)
  POST /chat                   -> grounded @-referenced chat (right pane)
"""

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

from config import CORS_ORIGINS, TOPIC
from models import (
    ChatRequest, ChatResponse, Graph, GraphLink, GraphNode,
    IngestUrlRequest, PaperOut,
)
from ai import answer_question
from ingest import convert_bytes, convert_url
from pipeline import ingest_paper
import store

app = FastAPI(title="SEALION")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    store.load()


def _to_out(p) -> PaperOut:
    return PaperOut(
        id=p.id, title=p.title, authors=p.authors, url=p.url,
        relevance_score=p.relevance_score, overview=p.overview, edges=p.edges,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "topic": TOPIC, "papers": len(store.all_sorted())}


@app.get("/papers", response_model=list[PaperOut])
def list_papers() -> list[PaperOut]:
    return [_to_out(p) for p in store.all_sorted()]


@app.get("/graph", response_model=Graph)
def graph() -> Graph:
    papers = store.all_sorted()
    ids = {p.id for p in papers}
    nodes = [GraphNode(id=p.id, name=p.title, relevance=p.relevance_score)
             for p in papers]
    links: list[GraphLink] = []
    seen: set[tuple[str, str]] = set()
    for p in papers:
        for target in p.edges:
            if target in ids:
                key = tuple(sorted((p.id, target)))
                if key not in seen and key[0] != key[1]:
                    seen.add(key)
                    links.append(GraphLink(source=key[0], target=key[1]))
    return Graph(nodes=nodes, links=links)


@app.post("/papers/ingest-url", response_model=PaperOut)
def ingest_url(req: IngestUrlRequest) -> PaperOut:
    try:
        markdown = convert_url(req.url)
    except Exception as e:
        raise HTTPException(400, f"Could not fetch/convert URL: {e}")
    # Live drops stay in-memory only; the seed is the sole writer of papers.json,
    # so every demo run starts from the same clean seeded workspace.
    paper = ingest_paper(markdown, url=req.url, persist=False)
    return _to_out(paper)


@app.post("/papers/upload", response_model=PaperOut)
async def upload(file: UploadFile = File(...)) -> PaperOut:
    data = await file.read()
    try:
        markdown = convert_bytes(data, filename=file.filename or "upload.pdf")
    except Exception as e:
        raise HTTPException(400, f"Could not convert PDF: {e}")
    paper = ingest_paper(markdown, url=None, pdf_bytes=data, persist=False)
    return _to_out(paper)


@app.get("/papers/{paper_id}/pdf")
def paper_pdf(paper_id: str):
    paper = store.get(paper_id)
    if paper is None:
        raise HTTPException(404, "No such paper")

    # Uploaded PDFs are served from memory.
    raw = store.get_pdf_bytes(paper_id)
    if raw is not None:
        return Response(content=raw, media_type="application/pdf")

    # URL-sourced papers are proxied same-origin (sidesteps arXiv iframe blocking).
    if paper.url:
        try:
            upstream = httpx.get(paper.url, follow_redirects=True, timeout=30)
            upstream.raise_for_status()
        except Exception as e:
            raise HTTPException(502, f"Could not proxy PDF: {e}")
        return Response(
            content=upstream.content,
            media_type=upstream.headers.get("content-type", "application/pdf"),
        )

    raise HTTPException(404, "No PDF available for this paper")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    referenced: list[tuple[str, str]] = []
    cited_ids: list[str] = []
    for pid in req.paper_ids:
        p = store.get(pid)
        if p is not None:
            referenced.append((p.title, p.markdown))
            cited_ids.append(pid)
    # The assistant is always aware of the whole library (title + overview),
    # so the user can ask about any paper by name/topic/author without tagging.
    catalog = [(p.title, p.authors, p.overview) for p in store.all_sorted()]
    answer = answer_question(req.question, referenced, catalog)
    return ChatResponse(answer=answer, cited_ids=cited_ids)
