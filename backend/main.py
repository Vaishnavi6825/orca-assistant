import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 📦 Load environment variables from .env
load_dotenv()

# ✅ Create FastAPI app
app = FastAPI()

# ✅ Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to ["http://localhost:5500"] if needed
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount static files at /static (not root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "static")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ✅ Simple root test route
@app.get("/")
async def root():
    return HTMLResponse("<h2>✅ FastAPI TTS backend is running</h2>")

# ✅ MURF API Key
MURF_API_KEY = os.getenv("MURF_API_KEY")

# ✅ Request model for TTS
class TTSRequest(BaseModel):
    text: str
    voiceId: str = "en-US-natalie"

# ✅ POST endpoint for TTS
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
