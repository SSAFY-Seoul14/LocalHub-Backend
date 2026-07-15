from pydantic import BaseModel
from typing import List, Optional

class MessageSchema(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    history: List[MessageSchema]
    category: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    success: bool = True