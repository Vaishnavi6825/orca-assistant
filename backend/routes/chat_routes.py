from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, List
import logging
from ..schemas.response import AgentChatResponse, ChatMessage
from ..services.assemblyai_service import transcribe_audio_bytes
from ..services.gemini_service import get_llm_response
from ..services.murf_service import generate_tts_audio
from ..config import FALLBACK_TEXT, FALLBACK_AUDIO_URL, MAX_CHAT_TURNS, MAX_CHAR_HISTORY

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

# In-memory chat history (for demonstration)
chat_history: Dict[str, List[ChatMessage]] = {}

def truncate_history(history: List[ChatMessage]) -> List[ChatMessage]:
    result = []
    total_chars = 0
    for msg in reversed(history):
        msg_text = f"{msg.role.upper()}: {msg.content}\n"
        if total_chars + len(msg_text) > MAX_CHAR_HISTORY:
            break
        result.insert(0, msg)
        total_chars += len(msg_text)
    
    if len(result) > MAX_CHAT_TURNS * 2:
        result = result[-MAX_CHAT_TURNS*2:]
    
    return result

@router.post("/agent/chat/{session_id}", response_model=AgentChatResponse)
async def agent_chat(session_id: str, file: UploadFile = File(...)):
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    # 1. Transcribe Audio
    try:
        user_audio_bytes = await file.read()
        user_text = transcribe_audio_bytes(user_audio_bytes)
        if not user_text:
            raise HTTPException(status_code=400, detail="No speech detected.")
    except HTTPException as e:
        return AgentChatResponse(user_text="", assistant_text=FALLBACK_TEXT, audio_url="", error=str(e), chat_history=[])
    except Exception as e:
        logger.error(f"STT failed in chat: {e}")
        return AgentChatResponse(user_text="", assistant_text=FALLBACK_TEXT, audio_url="", error=f"STT failed: {e}", chat_history=[])
    
    # 2. Get LLM Response
    try:
        chat_history[session_id].append(ChatMessage(role="user", content=user_text))
        
        # Truncate history before sending to LLM
        truncated_history = truncate_history(chat_history[session_id])
        
        prompt_with_history = "\n".join([f"{msg.role.upper()}: {msg.content}" for msg in truncated_history])
        llm_response_text = get_llm_response(prompt_with_history)
        
        chat_history[session_id].append(ChatMessage(role="assistant", content=llm_response_text))
        
        # Truncate history after adding new messages
        chat_history[session_id] = truncate_history(chat_history[session_id])
    except Exception as e:
        logger.error(f"LLM service failed in chat: {e}")
        return AgentChatResponse(user_text=user_text, assistant_text=FALLBACK_TEXT, audio_url="", error=f"LLM failed: {e}", chat_history=chat_history[session_id])

    # 3. Generate TTS Audio
    try:
        audio_url = generate_tts_audio(llm_response_text)
    except HTTPException as e:
        logger.error(f"TTS service failed in chat: {e}")
        audio_url = FALLBACK_AUDIO_URL
    
    return AgentChatResponse(
        user_text=user_text,
        assistant_text=llm_response_text,
        audio_url=audio_url,
        error=None,
        chat_history=chat_history[session_id]
    )
