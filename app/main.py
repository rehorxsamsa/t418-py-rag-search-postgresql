import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import settings
from app.database import Document, get_session, init_db
from app.routers import documents
from app.services.embeddings import get_embedding_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_DOCS = [
    ("Docker basics", "Docker packages applications into containers that share the host kernel but isolate dependencies, making deployments reproducible across environments."),
    ("Vector databases", "A vector database stores high-dimensional embeddings and retrieves the nearest neighbors using distance metrics like cosine similarity, powering semantic search."),
    ("Retrieval-Augmented Generation", "RAG retrieves relevant documents and feeds them to a language model as context, grounding answers in real data and reducing hallucinations."),
    ("FastAPI framework", "FastAPI is a modern Python web framework with automatic OpenAPI docs, async support, and type-based request validation via Pydantic."),
    ("PostgreSQL with pgvector", "The pgvector extension adds a vector column type to PostgreSQL, enabling similarity search directly in SQL without a separate vector store."),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Seed example data only if the table is empty.
    with get_session() as session:
        if session.query(Document).count() == 0:
            provider = get_embedding_provider()
            for title, content in SEED_DOCS:
                emb = provider.embed([f"{title}\n{content}"])[0]
                session.add(Document(title=title, content=content, embedding=emb))
            logger.info("Seeded %d example documents", len(SEED_DOCS))
    yield


app = FastAPI(
    title="Semantic Document Search",
    description="RAG demo: pgvector similarity search + Claude answer synthesis.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents.router, prefix="/api", tags=["documents"])


INDEX_HTML = """\
<!doctype html>
<html lang="cs">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>sémantické vyhledávání · RAG demo</title>
  <style>
    :root {
      --bg: #0a0e16; --panel: #111726; --panel-2: #0d1320;
      --border: #1e2738; --border-soft: #1a2230;
      --text: #d7dee9; --muted: #6b7689; --faint: #4b5567;
      --accent: #2dd4bf; --accent-soft: #134e4a; --accent-text: #5eead4;
      --mono: ui-monospace, "SF Mono", "JetBrains Mono", "Fira Code", monospace;
      --sans: system-ui, -apple-system, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0; background: var(--bg); color: var(--text);
      font: 15px/1.55 var(--sans);
      background-image: radial-gradient(900px 400px at 85% -10%, rgba(45,212,191,.07), transparent 60%);
    }
    .wrap { max-width: 1200px; margin: 0 auto; padding: 1.5rem 1.75rem 4rem; }

    header { display: flex; align-items: flex-start; justify-content: space-between;
      gap: 1rem; flex-wrap: wrap; padding: .5rem 0 1.75rem; }
    .brand h1 { margin: 0; font: 600 1.5rem/1.2 var(--mono); color: var(--accent-text);
      letter-spacing: -.01em; }
    .brand h1 .b { color: var(--faint); font-weight: 400; }
    .brand p { margin: .35rem 0 0; color: var(--muted); font-size: .85rem; }
    .chips { display: flex; gap: .5rem; flex-wrap: wrap; }
    .chip { font: 500 .72rem/1 var(--mono); color: var(--muted);
      border: 1px solid var(--border); background: var(--panel-2);
      padding: .5rem .7rem; border-radius: 999px; white-space: nowrap; }
    .chip.on { color: var(--accent-text); border-color: var(--accent-soft); }
    .chip .dot { color: var(--accent); }

    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; align-items: start; }
    .col { display: flex; flex-direction: column; gap: 1.25rem; }
    .panel { background: var(--panel); border: 1px solid var(--border);
      border-radius: 14px; padding: 1.25rem; }
    .label { font: 600 .72rem/1 var(--mono); letter-spacing: .12em;
      text-transform: uppercase; color: var(--faint); margin: 0 0 .9rem;
      display: flex; justify-content: space-between; align-items: center; }
    .label .count { color: var(--muted); }

    input, textarea {
      width: 100%; background: var(--panel-2); color: var(--text);
      border: 1px solid var(--border); border-radius: 9px; padding: .8rem .9rem;
      font: 15px/1.5 var(--sans); outline: none; transition: border-color .15s;
    }
    input::placeholder, textarea::placeholder { color: var(--faint); }
    input:focus, textarea:focus { border-color: var(--accent-soft); }
    textarea { resize: vertical; min-height: 110px; }

    .row { display: flex; align-items: center; gap: .6rem; margin-top: .9rem; }
    button { font: 600 .9rem var(--sans); border-radius: 9px; cursor: pointer;
      padding: .65rem 1.1rem; border: 1px solid transparent; transition: all .15s; }
    button:disabled { opacity: .5; cursor: progress; }
    .btn-primary { background: var(--accent); color: #06302b; }
    .btn-primary:hover:not(:disabled) { background: var(--accent-text); }
    .btn-ghost { background: transparent; color: var(--text); border-color: var(--border); }
    .btn-ghost:hover:not(:disabled) { border-color: var(--accent-soft); color: var(--accent-text); }
    .btn-block { width: 100%; justify-content: center; }
    .topk { margin-left: auto; display: flex; align-items: center; gap: .5rem;
      color: var(--faint); font: 600 .72rem var(--mono); text-transform: uppercase;
      letter-spacing: .08em; }
    .topk input { width: 56px; text-align: center; padding: .45rem; }

    .results { min-height: 96px; }
    .empty { color: var(--muted); text-align: center; padding: 2rem 1rem; font-size: .9rem; }
    .answer { background: var(--panel-2); border: 1px solid var(--accent-soft);
      border-radius: 10px; padding: 1rem; margin-bottom: 1rem; white-space: pre-wrap; }
    .answer .h { font: 600 .7rem var(--mono); letter-spacing: .1em; text-transform: uppercase;
      color: var(--accent-text); margin-bottom: .5rem; }
    .hit { padding: .85rem 0; border-top: 1px solid var(--border-soft); }
    .hit:first-child { border-top: 0; }
    .hit .t { display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }
    .hit .t strong { font-size: .98rem; }
    .hit .score { font: 600 .72rem var(--mono); color: var(--accent-text);
      background: var(--accent-soft); padding: .15rem .5rem; border-radius: 6px; white-space: nowrap; }
    .hit .c { color: var(--muted); font-size: .86rem; margin-top: .25rem; }

    .doc { padding: .9rem 0; border-top: 1px solid var(--border-soft);
      display: flex; justify-content: space-between; gap: .75rem; }
    .doc:first-child { border-top: 0; }
    .doc .t { font-weight: 600; }
    .doc .c { color: var(--muted); font-size: .84rem; margin-top: .2rem; }
    .doc .x { background: none; border: 0; color: var(--faint); font-size: 1.1rem;
      line-height: 1; padding: .1rem .4rem; cursor: pointer; }
    .doc .x:hover { color: #f87171; }
    .lib { max-height: 520px; overflow-y: auto; }
    .links { margin-top: 1rem; font: .78rem var(--mono); color: var(--faint); }
    .links a { color: var(--muted); text-decoration: none; }
    .links a:hover { color: var(--accent-text); }
    .toast { position: fixed; bottom: 1.25rem; left: 50%; transform: translateX(-50%);
      background: var(--panel); border: 1px solid var(--border); color: var(--text);
      padding: .7rem 1.1rem; border-radius: 9px; font-size: .85rem; opacity: 0;
      transition: opacity .2s; pointer-events: none; }
    .toast.show { opacity: 1; }
    @media (max-width: 820px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="brand">
        <h1><span class="b">&lt;</span>sémantické vyhledávání<span class="b">&gt;</span></h1>
        <p>Embeddingy · pgvector · RAG nad Claude — FastAPI / Python</p>
      </div>
      <div class="chips">
        <span class="chip">provider: __PROVIDER__ · __DIM__d</span>
        <span class="chip" id="chip-count">… dokumentů</span>
        <span class="chip __AI_CLS__"><span class="dot">●</span> AI: __AI_STATE__</span>
      </div>
    </header>

    <div class="grid">
      <div class="col">
        <section class="panel">
          <p class="label">Dotaz</p>
          <input id="q" placeholder="Na co se chcete zeptat dokumentů?"
                 autocomplete="off">
          <div class="row">
            <button class="btn-primary" id="btn-search">Hledat</button>
            <button class="btn-ghost" id="btn-ask">✦ Zeptat se AI</button>
            <span class="topk">top-k <input id="topk" type="number" min="1" max="10" value="5"></span>
          </div>
        </section>

        <section class="panel">
          <p class="label">Výsledky</p>
          <div class="results" id="results">
            <div class="empty">Zadejte dotaz a spusťte sémantické vyhledávání.</div>
          </div>
        </section>
      </div>

      <div class="col">
        <section class="panel">
          <p class="label">Přidat dokument</p>
          <input id="doc-title" placeholder="Název" autocomplete="off"
                 style="margin-bottom:.6rem">
          <textarea id="doc-content" placeholder="Obsah dokumentu…"></textarea>
          <div class="row">
            <button class="btn-primary btn-block" id="btn-add">Uložit a zaembeddovat</button>
          </div>
        </section>

        <section class="panel">
          <p class="label">Knihovna dokumentů <span class="count" id="lib-count"></span></p>
          <div class="lib" id="library"><div class="empty">Načítám…</div></div>
        </section>

        <div class="links">
          <a href="/docs">/docs</a> · <a href="/redoc">/redoc</a> ·
          <a href="/health">/health</a> · <a href="/openapi.json">/openapi.json</a>
        </div>
      </div>
    </div>
  </div>
  <div class="toast" id="toast"></div>

<script>
const $ = s => document.querySelector(s);
const esc = s => (s ?? "").replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), 2200);
}

async function loadLibrary() {
  try {
    const docs = await (await fetch("/api/documents")).json();
    const lib = $("#library");
    $("#lib-count").textContent = docs.length;
    $("#chip-count").textContent = docs.length + " dokument" +
      (docs.length === 1 ? "" : (docs.length >= 2 && docs.length <= 4 ? "y" : "ů"));
    if (!docs.length) { lib.innerHTML = '<div class="empty">Zatím žádné dokumenty.</div>'; return; }
    lib.innerHTML = docs.map(d => `
      <div class="doc">
        <div>
          <div class="t">${esc(d.title)}</div>
          <div class="c">${esc((d.content || "").slice(0, 110))}${(d.content||"").length>110?"…":""}</div>
        </div>
        <button class="x" title="Smazat" data-id="${d.id}">×</button>
      </div>`).join("");
    lib.querySelectorAll(".x").forEach(b =>
      b.onclick = () => removeDoc(b.dataset.id));
  } catch (e) { $("#library").innerHTML = '<div class="empty">Chyba načítání.</div>'; }
}

async function removeDoc(id) {
  await fetch("/api/documents/" + id, { method: "DELETE" });
  toast("Dokument smazán"); loadLibrary();
}

function renderHits(results) {
  if (!results.length) return '<div class="empty">Nic nenalezeno.</div>';
  return results.map(r => `
    <div class="hit">
      <div class="t"><strong>${esc(r.title)}</strong>
        <span class="score">${(r.score*100).toFixed(1)} %</span></div>
      <div class="c">${esc(r.content)}</div>
    </div>`).join("");
}

async function doSearch() {
  const q = $("#q").value.trim(); if (!q) return;
  const k = $("#topk").value || 5;
  const btn = $("#btn-search"); btn.disabled = true;
  $("#results").innerHTML = '<div class="empty">Hledám…</div>';
  try {
    const data = await (await fetch(`/api/search?q=${encodeURIComponent(q)}&top_k=${k}`)).json();
    $("#results").innerHTML = renderHits(data.results);
  } catch (e) { $("#results").innerHTML = '<div class="empty">Chyba vyhledávání.</div>'; }
  finally { btn.disabled = false; }
}

async function doAsk() {
  const q = $("#q").value.trim(); if (!q) return;
  const k = parseInt($("#topk").value || "5", 10);
  const btn = $("#btn-ask"); btn.disabled = true;
  $("#results").innerHTML = '<div class="empty">Claude přemýšlí…</div>';
  try {
    const data = await (await fetch("/api/ask", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ query: q, top_k: k })
    })).json();
    const sources = (data.sources || []).map(s => `[${s.id}] ${esc(s.title)}`).join(" · ");
    $("#results").innerHTML =
      `<div class="answer"><div class="h">✦ Odpověď AI</div>${esc(data.answer)}</div>` +
      (sources ? `<div class="hit"><div class="c">Zdroje: ${sources}</div></div>` : "");
  } catch (e) { $("#results").innerHTML = '<div class="empty">Chyba dotazu na AI.</div>'; }
  finally { btn.disabled = false; }
}

async function addDoc() {
  const title = $("#doc-title").value.trim();
  const content = $("#doc-content").value.trim();
  if (!title || !content) { toast("Vyplňte název i obsah"); return; }
  const btn = $("#btn-add"); btn.disabled = true;
  try {
    const r = await fetch("/api/documents", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ title, content })
    });
    if (!r.ok) throw new Error();
    $("#doc-title").value = ""; $("#doc-content").value = "";
    toast("Dokument uložen a zaembeddován"); loadLibrary();
  } catch (e) { toast("Uložení selhalo"); }
  finally { btn.disabled = false; }
}

$("#btn-search").onclick = doSearch;
$("#btn-ask").onclick = doAsk;
$("#btn-add").onclick = addDoc;
$("#q").addEventListener("keydown", e => { if (e.key === "Enter") doSearch(); });
loadLibrary();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def index():
    ai_on = bool(settings.anthropic_api_key)
    html = (
        INDEX_HTML
        .replace("__PROVIDER__", settings.embedding_provider)
        .replace("__DIM__", str(settings.embedding_dim))
        .replace("__AI_STATE__", "zapnuto" if ai_on else "vypnuto")
        .replace("__AI_CLS__", "on" if ai_on else "")
    )
    return html


@app.get("/health")
def health():
    return {"status": "ok"}
