This directory holds all the Pydantic models used for API request and response validation.

1. request.py: Defines the expected structure of incoming data (e.g., TTSRequest, LLMRequest).


from pydantic import BaseModel
from typing import Optional

class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"

class LLMRequest(BaseModel):
    prompt: str

class ConversationalRequest(BaseModel):
    # This will be handled by UploadFile, but a good practice to define
    # a model if you were using a JSON body.
    pass

class ChatRequest(BaseModel):
    audio_file: Optional[bytes] = None
