from datetime import datetime

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., min_length=1)


class DocumentOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    score: float  # cosine similarity (1 = identical)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]
