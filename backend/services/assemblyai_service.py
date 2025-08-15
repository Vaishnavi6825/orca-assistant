import assemblyai as aai
import tempfile
import os
import logging
from fastapi import HTTPException
from ..config import ASSEMBLYAI_API_KEY

logger = logging.getLogger("uvicorn.error")

def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    if not ASSEMBLYAI_API_KEY:
        logger.error("ASSEMBLYAI_API_KEY is not set.")
        raise HTTPException(status_code=503, detail="ASSEMBLYAI_API_KEY is missing.")

    aai.settings.api_key = ASSEMBLYAI_API_KEY
    transcriber = aai.Transcriber()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        transcript = transcriber.transcribe(temp_path)
        return transcript.text.strip() if transcript and transcript.text else ""
    finally:
        os.remove(temp_path)
