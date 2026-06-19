import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

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


@app.get("/health")
def health():
    return {"status": "ok"}
