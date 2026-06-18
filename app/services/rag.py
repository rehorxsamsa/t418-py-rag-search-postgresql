"""Retrieval-Augmented Generation: vector search + Claude answer synthesis.

This is the piece most relevant to an AI-developer interview: it shows the full
RAG loop — embed query, retrieve nearest documents, ground the LLM on them, and
ask it to answer using only that context (reducing hallucination).
"""

from anthropic import Anthropic

from app.config import settings
from app.database import Document, get_session
from app.services.embeddings import get_embedding_provider


def retrieve(query: str, top_k: int = 3) -> list[Document]:
    """Return the top_k documents most similar to the query by cosine distance."""
    query_vec = get_embedding_provider().embed([query])[0]
    with get_session() as session:
        return (
            session.query(Document)
            .order_by(Document.embedding.cosine_distance(query_vec))
            .limit(top_k)
            .all()
        )


def answer(query: str, top_k: int = 3) -> dict:
    """RAG: retrieve context, then have Claude answer grounded in it."""
    docs = retrieve(query, top_k)

    if not settings.anthropic_api_key:
        # Graceful degradation: still useful as pure semantic search without a key.
        return {
            "answer": "(LLM disabled — set ANTHROPIC_API_KEY to enable answers.)",
            "sources": [{"id": d.id, "title": d.title} for d in docs],
        }

    context = "\n\n".join(f"[{d.id}] {d.title}\n{d.content}" for d in docs)
    client = Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=(
            "You answer strictly from the provided context. "
            "If the answer is not in the context, say so. "
            "Cite sources using their [id]."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            }
        ],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    return {
        "answer": text,
        "sources": [{"id": d.id, "title": d.title} for d in docs],
    }
