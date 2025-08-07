import os
import requests
from datetime import datetime
import shutil

import assemblyai as aai

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

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

# ✅ Mount static directories
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ✅ Serve index.html on root URL
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# ✅ Load MURF API Key
MURF_API_KEY = os.getenv("MURF_API_KEY")

# ✅ TTS request model
class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"

# ✅ POST endpoint for generating TTS
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
        response = requests.post("https://api.murf.ai/v1/speech/generate", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ POST endpoint for uploading audio files
@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{now}_{file.filename}")

    # Save the uploaded file
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_size = os.path.getsize(file_path)
    print(f"✅ Uploaded: {file.filename} → {file_path}")

    return {
        "filename": os.path.basename(file_path),
        "content_type": file.content_type,
        "size": file_size
    }

# 🔐 Load API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
transcriber = aai.Transcriber()

# 🧠 Transcribe uploaded audio (no need to save it)
@app.post("/transcribe/file")
async def transcribe_file(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()  # read the audio as bytes
        transcript = transcriber.transcribe(audio_bytes)  # transcribe with SDK
        return {"transcript": transcript.text}  # return just the transcript text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))