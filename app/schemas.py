"""Pydantic schemas used by API endpoints."""
from pydantic import BaseModel
from typing import Optional


class QueryPayload(BaseModel):
    user_id: int
    question: str


class QueryResponse(BaseModel):
    result: Optional[str]


class ErrorResponse(BaseModel):
    error: str


class MessageResponse(BaseModel):
    message: str


class LLMErrorResponse(BaseModel):
    error: str = "LLM unavailable"
