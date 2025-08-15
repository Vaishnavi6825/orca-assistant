This directory organizes the API endpoints into logical groups. Each file represents a different set of related endpoints.

1.tts_routes.py: Contains endpoints related to basic TTS generation, audio uploads, and transcription, which can be used as standalone utilities or by other parts of the application.

from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os
from datetime import datetime
import logging
from ..schemas.request import TTSRequest
from ..schemas.response import TTSResponse, TranscriptionResponse
from ..services.murf_service import generate_tts_audio
from ..services.assemblyai_service import transcribe_audio_bytes
from ..config import FALLBACK_AUDIO_URL, UPLOAD_DIR

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

@router.post("/tts", response_model=TTSResponse)
async def generate_tts(request: TTSRequest):
    audio_url = generate_tts_audio(text=request.text, voice_id=request.voiceId)
    return TTSResponse(audioFile=audio_url)

@router.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(UPLOAD_DIR, f"{now}_{file.filename}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": os.path.basename(file_path),
            "content_type": file.content_type,
            "size": os.path.getsize(file_path)}

@router.post("/transcribe/file", response_model=TranscriptionResponse)
async def transcribe_file(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        text = transcribe_audio_bytes(audio_bytes)
        if not text:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")
        return TranscriptionResponse(transcript=text)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"STT failed: {e}")
        raise HTTPException(status_code=503, detail=f"Speech-to-Text failed: {str(e)}")
