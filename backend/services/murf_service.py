This directory contains the business logic for interacting with external APIs. Each service is in its own file, which promotes code reuse and makes it easy to swap out one service for another in the future.
murf_service.py: Contains the logic for converting text responses into audio using the Murf TTS API.

import requests
import logging
from fastapi import HTTPException
from ..config import MURF_API_KEY, FALLBACK_AUDIO_URL, FALLBACK_TEXT
from ..schemas.request import TTSRequest

logger = logging.getLogger("uvicorn.error")

def generate_tts_audio(text: str, voice_id: str = "en-US-natalie"):
    if not MURF_API_KEY:
        logger.error("MURF_API_KEY is not set.")
        raise HTTPException(status_code=503, detail="MURF_API_KEY is missing.")

    try:
        headers = {"api-key": MURF_API_KEY, "Content-Type": "application/json"}
        payload = {"text": text, "voiceId": voice_id}
        response = requests.post(
            "https://api.murf.ai/v1/speech/generate",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        murf_data = response.json()
        audio_url = murf_data.get("audioFile") or FALLBACK_AUDIO_URL
        return audio_url
    except requests.RequestException as e:
        logger.error(f"Murf TTS service failed: {e}")
        return FALLBACK_AUDIO_URL
