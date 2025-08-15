gemini_service.py: Handles all interactions with the Google Gemini LLM to generate conversational responses.

import google.generativeai as genai
import logging
from fastapi import HTTPException
from typing import List, Dict
from ..config import GEMINI_API_KEY, FALLBACK_TEXT

logger = logging.getLogger("uvicorn.error")

def get_llm_response(prompt: str) -> str:
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set.")
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is missing.")

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-pro")
        resp = model.generate_content(prompt)
        llm_text = getattr(resp, "text", "").strip()
        return llm_text or FALLBACK_TEXT
    except Exception as e:
        logger.error(f"Gemini LLM service failed: {e}")
        return FALLBACK_TEXT
