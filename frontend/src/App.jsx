import { useEffect, useRef, useState } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { api } from "./api";
import "./App.css";

const TOPIC = "Mechanistic Interpretability";

export default function App() {
  const [papers, setPapers] = useState([]);
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [selected, setSelected] = useState(null); // paper object → PDF view
  const [refIds, setRefIds] = useState(() => new Set());
  const [url, setUrl] = useState("");
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    const [p, g] = await Promise.all([api.listPapers(), api.graph()]);
    setPapers(p);
    setGraph(g);
  }

  useEffect(() => {
    refresh().catch((e) => setError(e.message));
  }, []);

  async function addUrl() {
    if (!url.trim()) return;
    setAdding(true);
    setError("");
    try {
      await api.ingestUrl(url.trim());
      setUrl("");
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setAdding(false);
    }
  }

  async function addFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setAdding(true);
    setError("");
    try {
      await api.uploadPdf(file);
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setAdding(false);
      e.target.value = "";
    }
  }

  function toggleRef(id) {
    setRefIds((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  const byId = Object.fromEntries(papers.map((p) => [p.id, p]));

  return (
    <div className="app">
      <div className="topbar">
        <span className="wordmark">SEALION</span>
        <span className="topic-pill">{TOPIC}</span>
      </div>

      <div className="panes">
        <LeftLibrary
          papers={papers}
          selected={selected}
          onSelect={setSelected}
          refIds={refIds}
          onToggleRef={toggleRef}
          url={url}
          setUrl={setUrl}
          adding={adding}
          onAddUrl={addUrl}
          onAddFile={addFile}
          error={error}
        />

        <MiddlePane
          graph={graph}
          selected={selected}
          byId={byId}
          onSelect={setSelected}
        />

        <RightChat
          refIds={refIds}
          byId={byId}
          onToggleRef={toggleRef}
        />
      </div>
    </div>
  );
}

function LeftLibrary(props) {
  const {
    papers, selected, onSelect, refIds, onToggleRef,
    url, setUrl, adding, onAddUrl, onAddFile, error,
  } = props;
  const fileRef = useRef(null);

  return (
    <div className="pane left">
      <div className="pane-head">Library · {papers.length}</div>

      <div className="add-row">
        <input
          type="text"
          placeholder="Paste a paper URL…"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onAddUrl()}
        />
        <button className="btn-primary" onClick={onAddUrl} disabled={adding}>
          {adding ? "…" : "Add"}
        </button>
      </div>
      <div className="add-row" style={{ borderBottom: "1px solid var(--hairline-soft)" }}>
        <button className="btn-ghost" onClick={() => fileRef.current?.click()} disabled={adding}>
          Upload PDF
        </button>
        <input ref={fileRef} type="file" accept="application/pdf" hidden onChange={onAddFile} />
      </div>

      {error && <div className="err">{error}</div>}

      <div className="pane-scroll">
        {papers.length === 0 && (
          <div className="hint">No papers yet. Paste a URL or upload a PDF to ingest one.</div>
        )}
        {papers.map((p) => (
          <div
            key={p.id}
            className={"paper" + (selected?.id === p.id ? " selected" : "")}
            onClick={() => onSelect(p)}
          >
            <div className="paper-title">{p.title}</div>
            <div className="paper-overview">{p.overview}</div>
            <div className="relrow">
              <div className="relbar"><span style={{ width: `${p.relevance_score}%` }} /></div>
              <div className="relnum">{p.relevance_score}</div>
            </div>
            <button
              className={"ref-toggle" + (refIds.has(p.id) ? " on" : "")}
              onClick={(e) => { e.stopPropagation(); onToggleRef(p.id); }}
            >
              {refIds.has(p.id) ? "@ referenced" : "@ reference"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function MiddlePane({ graph, selected, byId, onSelect }) {
  const wrapRef = useRef(null);
  const [dim, setDim] = useState({ w: 0, h: 0 });

  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setDim({ w: width, h: height });
    });
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, [selected]);

  if (selected) {
    return (
      <div className="pane">
        <div className="pdf-head">
          <button className="btn-ghost" onClick={() => onSelect(null)}>← Graph</button>
          <span className="t">{selected.title}</span>
        </div>
        <iframe className="pdf-frame" title="paper" src={api.pdfUrl(selected.id)} />
      </div>
    );
  }

  return (
    <div className="pane">
      <div className="pane-head">Knowledge Graph</div>
      <div className="graph-wrap" ref={wrapRef}>
        {graph.nodes.length === 0 ? (
          <div className="empty">
            The knowledge graph builds itself as papers are ingested.<br />
            Each node is a paper; edges are AI-derived topical links.
          </div>
        ) : (
          <ForceGraph2D
            width={dim.w}
            height={dim.h}
            graphData={graph}
            backgroundColor="#fafaf7"
            nodeRelSize={5}
            linkColor={() => "#cfcdc4"}
            linkWidth={1}
            onNodeClick={(node) => { const p = byId[node.id]; if (p) onSelect(p); }}
            nodeCanvasObject={(node, ctx, scale) => {
              const r = 4 + (node.relevance / 100) * 6;
              ctx.beginPath();
              ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
              ctx.fillStyle = "#26251e";
              ctx.fill();
              const label = node.name.length > 32 ? node.name.slice(0, 32) + "…" : node.name;
              const fs = 11 / scale;
              ctx.font = `${fs}px Inter, sans-serif`;
              ctx.fillStyle = "#5a5852";
              ctx.textAlign = "center";
              ctx.fillText(label, node.x, node.y + r + fs + 1);
            }}
          />
        )}
      </div>
    </div>
  );
}

function RightChat({ refIds, byId, onToggleRef }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, sending]);

  async function send() {
    const q = input.trim();
    if (!q || sending) return;
    const ids = [...refIds];
    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setSending(true);
    try {
      const res = await api.chat(q, ids);
      const cited = res.cited_ids.map((id) => byId[id]?.title).filter(Boolean);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, cites: cited }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: "Error: " + e.message }]);
    } finally {
      setSending(false);
    }
  }

  const refs = [...refIds].map((id) => byId[id]).filter(Boolean);

  return (
    <div className="pane right">
      <div className="pane-head">Chat · grounded in @-referenced papers</div>

      <div className="chat-scroll" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="hint">
            Tag papers with <b>@ reference</b> in the library, then ask a question.
            Answers are grounded in those papers' actual content.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={"msg " + m.role}>
            {m.text}
            {m.cites?.length > 0 && (
              <div className="cites">cited: {m.cites.join(" · ")}</div>
            )}
          </div>
        ))}
        {sending && <div className="spin">thinking…</div>}
      </div>

      {refs.length > 0 && (
        <div className="refchips">
          {refs.map((p) => (
            <span key={p.id} className="chip">
              <span className="label">@ {p.title}</span>
              <span className="x" onClick={() => onToggleRef(p.id)}>×</span>
            </span>
          ))}
        </div>
      )}

      <div className="chat-input">
        <textarea
          placeholder="Ask about the referenced papers…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
          }}
        />
        <button className="btn-primary" onClick={send} disabled={sending}>Send</button>
      </div>
    </div>
  );
}
