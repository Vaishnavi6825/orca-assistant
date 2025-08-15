This directory holds all the Pydantic models used for API request and response validation.

2.Defines the structure of the data sent back to the client, ensuring consistent API responses.

from pydantic import BaseModel
from typing import List, Dict, Any

class LLMResponse(BaseModel):
    response: str

class TTSResponse(BaseModel):
    audioFile: str
    error: Optional[str] = None

class TranscriptionResponse(BaseModel):
    transcript: str

class ChatMessage(BaseModel):
    role: str
    content: str

class AgentChatResponse(BaseModel):
    user_text: str
    assistant_text: str
    audio_url: str
    error: Optional[str] = None
    chat_history: List[ChatMessage]
