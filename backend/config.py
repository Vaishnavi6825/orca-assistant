import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
MURF_API_KEY = os.getenv("MURF_API_KEY", "").strip()
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Other Configurations
FALLBACK_AUDIO_URL = (
    "https://murf.ai/user-upload/one-day-temp/63ad7907-8d57-43c9-acc3-8544d19c14e1.wav"
)
FALLBACK_TEXT = "I'm having trouble connecting right now. Please try again later."
MAX_CHAT_TURNS = 10
MAX_CHAR_HISTORY = 4000

