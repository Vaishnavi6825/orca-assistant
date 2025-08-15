import os
import requests
import shutil
import tempfile
import logging
from datetime import datetime
from typing import Dict, List

import assemblyai as aai
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 📦 Load environment variables from .env
load_dotenv()
logger = logging.getLogger("uvicorn.error")

# ✅ Create FastAPI app
app = FastAPI()

# ✅ Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Define directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# ✅ Ensure directories exist before mounting
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
else:
    logger.warning("Static frontend directory not found — skipping /static mount.")

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ✅ Serve index.html on root URL
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Frontend not found</h1>")

# ✅ Load API Keys and validate
MURF_API_KEY = os.getenv("MURF_API_KEY", "").strip()
ASSEMBLY_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

def require_key(key: str, name: str):
    if not key:
        raise HTTPException(status_code=503, detail=f"Missing {name}")

# Fallback audio URL for TTS failures
FALLBACK_AUDIO_URL = (
    "https://murf.ai/user-upload/one-day-temp/63ad7907-8d57-43c9-acc3-8544d19c14e1.wav"
)
FALLBACK_TEXT = "I'm having trouble connecting right now. Please try again later."

# ✅ Request models
class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"

class LLMRequest(BaseModel):
    prompt: str

# Helper function to get fallback audio
def get_fallback_response(error_message: str):
    return {
        "user_text": "",
        "assistant_text": FALLBACK_TEXT,
        "audio_url": FALLBACK_AUDIO_URL,
        "error": error_message
    }

# Helper for AssemblyAI transcription (always via temp file)
def transcribe_audio(audio_bytes: bytes):
    require_key(ASSEMBLY_API_KEY, "ASSEMBLY_API_KEY")
    aai.settings.api_key = ASSEMBLY_API_KEY
    transcriber = aai.Transcriber()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name
    try:
        transcript = transcriber.transcribe(temp_path)
        return transcript.text.strip() if transcript and transcript.text else ""
    finally:
        os.remove(temp_path)

# ✅ POST endpoint for generating TTS
@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    require_key(MURF_API_KEY, "MURF_API_KEY")
    try:
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        payload = {"text": request.text, "voiceId": request.voiceId}
        response = requests.post("https://api.murf.ai/v1/speech/generate",
                                 headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"TTS service failed: {e}")
        return {"audioFile": FALLBACK_AUDIO_URL,
                "error": f"TTS service failed: {str(e)}. Returned fallback audio."}

# ✅ POST endpoint for uploading audio files
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{now}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": os.path.basename(file_path),
            "content_type": file.content_type,
            "size": os.path.getsize(file_path)}

# 🧠 Transcribe uploaded audio
@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        text = transcribe_audio(audio_bytes)
        if not text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")
        return {"transcript": text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT failed: {e}")
        raise HTTPException(status_code=503, detail=f"Speech-to-Text failed: {str(e)}")

# 🎯 Echo endpoint
@app.post("/tts/echo")
async def tts_echo(file: UploadFile = File(...)):
    try:
        user_text = transcribe_audio(await file.read())
        if not user_text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")
        logger.info(f"Transcript: {user_text}")

        require_key(MURF_API_KEY, "MURF_API_KEY")
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        payload = {"text": user_text, "voiceId": "en-US-natalie", "format": "mp3"}
        murf_resp = requests.post("https://api.murf.ai/v1/speech/generate",
                                  headers=headers, json=payload, timeout=60)
        murf_resp.raise_for_status()
        murf_data = murf_resp.json()
        audio_url = murf_data.get("audioFile") or FALLBACK_AUDIO_URL
        return {"audio_url": audio_url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Echo TTS failed: {e}")
        return {"audio_url": FALLBACK_AUDIO_URL,
                "error": f"TTS service failed: {str(e)}. Returned fallback audio."}

# 🧠 LLM Query Endpoint
@app.post("/llm/query")
async def llm_query(request: LLMRequest):
    require_key(GEMINI_API_KEY, "GEMINI_API_KEY")
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        resp = model.generate_content(request.prompt)
        llm_text = getattr(resp, "text", "").strip() or FALLBACK_TEXT
        return {"response": llm_text}
    except Exception as e:
        logger.error(f"LLM service failed: {e}")
        raise HTTPException(status_code=503, detail=f"LLM service failed: {str(e)}")

# 🆕 Audio → Transcription → LLM → TTS
@app.post("/llm/query/audio")
async def llm_query_audio(file: UploadFile = File(...)):
    try:
        user_text = transcribe_audio(await file.read())
        if not user_text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")

        require_key(GEMINI_API_KEY, "GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        llm_resp = model.generate_content(user_text)
        llm_text = getattr(llm_resp, "text", "").strip() or FALLBACK_TEXT

        # TTS with fallback
        try:
            require_key(MURF_API_KEY, "MURF_API_KEY")
            headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
            payload = {"text": llm_text, "voiceId": "en-US-natalie", "format": "mp3"}
            murf_resp = requests.post("https://api.murf.ai/v1/speech/generate",
                                      headers=headers, json=payload, timeout=60)
            murf_resp.raise_for_status()
            murf_data = murf_resp.json()
            audio_url = murf_data.get("audioFile") or FALLBACK_AUDIO_URL
        except Exception as tts_err:
            logger.error(f"TTS failed in llm_query_audio: {tts_err}")
            audio_url = FALLBACK_AUDIO_URL

        return {"transcript": user_text,
                "llm_response": llm_text,
                "audio_url": audio_url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=503, detail=f"Processing failed: {str(e)}")

# 🆕 Chat history + conversational memory
chat_history: Dict[str, List[Dict[str, str]]] = {}
MAX_TURNS = 10

def truncate_history_by_chars(history, max_chars=4000):
    result = []
    total = 0
    for msg in reversed(history):
        msg_text = f"{msg['role'].upper()}: {msg['content']}\n"
        if total + len(msg_text) > max_chars:
            break
        result.insert(0, msg)
        total += len(msg_text)
    return result

@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, file: UploadFile = File(...)):
    if session_id not in chat_history:
        chat_history[session_id] = []

    user_text = ""
    llm_response = ""

    try:
        user_text = transcribe_audio(await file.read())
        if not user_text:
            return get_fallback_response("No speech detected in audio.")
    except Exception as e:
        logger.error(f"STT failed in chat: {e}")
        return get_fallback_response(f"Speech-to-Text failed: {str(e)}")

    # --- PATCH: Do NOT add user message to history yet ---
    temp_history = chat_history[session_id] + [{"role": "user", "content": user_text}]
    temp_history = truncate_history_by_chars(temp_history, max_chars=4000)
    if len(temp_history) > MAX_TURNS * 2:
        temp_history = temp_history[-MAX_TURNS*2:]

    try:
        require_key(GEMINI_API_KEY, "GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        conversation_text = "\n".join(f"{msg['role'].upper()}: {msg['content']}"
                                      for msg in temp_history)
        llm_resp = model.generate_content(conversation_text)
        llm_response = getattr(llm_resp, "text", "").strip() or FALLBACK_TEXT
    except Exception as e:
        logger.error(f"LLM service failed in chat: {e}")
        return get_fallback_response(f"LLM service failed: {str(e)}")

    # Only now add to real chat history
    chat_history[session_id].append({"role": "user", "content": user_text})
    chat_history[session_id].append({"role": "assistant", "content": llm_response})

    if len(chat_history[session_id]) > MAX_TURNS * 2:
        chat_history[session_id] = chat_history[session_id][-MAX_TURNS*2:]

    try:
        require_key(MURF_API_KEY, "MURF_API_KEY")
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        payload = {"text": llm_response, "voiceId": "en-US-natalie", "format": "mp3"}
        murf_resp = requests.post("https://api.murf.ai/v1/speech/generate",
                                  headers=headers, json=payload, timeout=60)
        murf_resp.raise_for_status()
        murf_data = murf_resp.json()
        audio_url = murf_data.get("audioFile") or FALLBACK_AUDIO_URL
    except Exception as tts_err:
        logger.error(f"TTS failed in chat: {tts_err}")
        return {"user_text": user_text,
                "assistant_text": llm_response,
                "audio_url": FALLBACK_AUDIO_URL,
                "error": f"TTS service failed: {str(tts_err)}. Returned fallback audio.",
                "chat_history": chat_history[session_id]
                }

    return {"user_text": user_text,
            "assistant_text": llm_response,
            "audio_url": audio_url,
            "chat_history": chat_history[session_id]}
