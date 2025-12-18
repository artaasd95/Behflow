from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
