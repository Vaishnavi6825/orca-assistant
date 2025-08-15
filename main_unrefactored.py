import os
import requests
from datetime import datetime
import shutil

import assemblyai as aai
import google.generativeai as genai

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import tempfile  # ⬅️ Day 9 addition

# 📦 Load environment variables from .env
load_dotenv()

# ✅ Create FastAPI app
app = FastAPI()

# ✅ Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
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

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ✅ Serve index.html on root URL
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    return HTMLResponse("<h1>Frontend not found</h1>")

# ✅ Load MURF API Key
MURF_API_KEY = os.getenv("MURF_API_KEY")

# ✅ Request models
class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"

class LLMRequest(BaseModel):
    prompt: str

# ✅ POST endpoint for generating TTS (Day 7)
@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    try:
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": request.text,
            "voiceId": request.voiceId
        }
        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ POST endpoint for uploading audio files (Day 7)
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{now}_{file.filename}")

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)
    print(f"✅ Uploaded: {file.filename} → {file_path}")

    return {
        "filename": os.path.basename(file_path),
        "content_type": file.content_type,
        "size": file_size
    }

# 🔐 AssemblyAI setup moved inside endpoints to prevent startup blocking
ASSEMBLY_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# 🧠 Transcribe uploaded audio (Day 7)
@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        aai.settings.api_key = ASSEMBLY_API_KEY
        transcriber = aai.Transcriber()
        audio_bytes = await file.read()
        transcript = transcriber.transcribe(audio_bytes)
        return {"transcript": transcript.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🎯 Echo endpoint (Day 7)
@app.post("/tts/echo")
async def tts_echo(file: UploadFile = File(...)):
    try:
        aai.settings.api_key = ASSEMBLY_API_KEY
        transcriber = aai.Transcriber()
        audio_bytes = await file.read()

        transcript = transcriber.transcribe(audio_bytes)
        if not transcript.text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")

        text_to_speak = transcript.text
        print(f"📝 Transcript: {text_to_speak}")

        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text_to_speak,
            "voiceId": "en-US-natalie",
            "format": "mp3"
        }
        murf_resp = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )
        murf_resp.raise_for_status()
        murf_data = murf_resp.json()

        return {"audio_url": murf_data.get("audioFile")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧠 Day 8: LLM Query Endpoint (text input)
@app.post("/llm/query")
async def llm_query(request: LLMRequest):
    try:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            raise HTTPException(status_code=500, detail="Missing GEMINI_API_KEY")

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(request.prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 🆕 Day 9: Audio → Transcription → LLM → Murf TTS
@app.post("/llm/query/audio")
async def llm_query_audio(file: UploadFile = File(...)):
    try:
        # Step 1: Transcription
        aai.settings.api_key = ASSEMBLY_API_KEY
        transcriber = aai.Transcriber()
        audio_bytes = await file.read()
        transcript = transcriber.transcribe(audio_bytes)
        if not transcript.text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")

        # Step 2: LLM
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        llm_response = model.generate_content(transcript.text).text.strip()

        # Step 3: Murf TTS
        headers = {
            "api-key": MURF_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": llm_response,
            "voiceId": "en-US-natalie",
            "format": "mp3"
        }
        murf_resp = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload
        )
        murf_resp.raise_for_status()
        murf_data = murf_resp.json()

        return {
            "transcript": transcript.text,
            "llm_response": llm_response,
            "audio_url": murf_data.get("audioFile")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
