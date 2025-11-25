from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3.2"

class ChatResponse(BaseModel):
    thinking: Optional[str] = None
    response: str

