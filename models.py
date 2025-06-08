from typing import Optional, List

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class SourceInfo(BaseModel):
    source: str
    type: str
    title: Optional[str] = ""


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: str
    similar_questions: Optional[List[str]] = []


class HealthResponse(BaseModel):
    status: str
    vector_store_loaded: bool
    total_documents: int
    test_query_successful: bool
    error: Optional[str] = None