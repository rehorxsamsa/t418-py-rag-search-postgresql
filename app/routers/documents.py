from fastapi import APIRouter, HTTPException

from app.database import Document, get_session
from app.schemas import (
    AskRequest,
    AskResponse,
    DocumentIn,
    DocumentOut,
    SearchResponse,
    SearchResult,
)
from app.services.embeddings import get_embedding_provider
from app.services.rag import answer

router = APIRouter()


@router.post("/documents", response_model=DocumentOut, status_code=201)
def create_document(doc: DocumentIn):
    """Embed and store a document."""
    embedding = get_embedding_provider().embed([f"{doc.title}\n{doc.content}"])[0]
    with get_session() as session:
        db_doc = Document(title=doc.title, content=doc.content, embedding=embedding)
        session.add(db_doc)
        session.flush()
        return DocumentOut.model_validate(db_doc)


@router.get("/documents", response_model=list[DocumentOut])
def list_documents():
    with get_session() as session:
        return [DocumentOut.model_validate(d) for d in session.query(Document).all()]


@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(doc_id: int):
    with get_session() as session:
        doc = session.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        session.delete(doc)


@router.get("/search", response_model=SearchResponse)
def search(q: str, top_k: int = 5):
    """Pure semantic search — returns ranked documents with similarity scores."""
    query_vec = get_embedding_provider().embed([q])[0]
    with get_session() as session:
        rows = (
            session.query(
                Document,
                Document.embedding.cosine_distance(query_vec).label("distance"),
            )
            .order_by("distance")
            .limit(top_k)
            .all()
        )
        results = [
            SearchResult(
                id=doc.id,
                title=doc.title,
                content=doc.content,
                score=round(1 - distance, 4),  # distance -> similarity
            )
            for doc, distance in rows
        ]
    return SearchResponse(query=q, results=results)


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """RAG endpoint: semantic retrieval + Claude-generated grounded answer."""
    result = answer(req.query, req.top_k)
    return AskResponse(**result)
