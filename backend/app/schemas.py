from pydantic import BaseModel, Field, validator
from typing import Optional, List

class Message(BaseModel):
    role:str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = 'default'

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[str]]=[]
    processing_time_ms: Optional[float] =None


