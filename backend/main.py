import os
import asyncio
import json
import logging
import time
import re
from datetime import datetime
import requests

# --- Third-Party Imports ---
import assemblyai as aai
import google.generativeai as genai
import websockets
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --------------------------------------------------------------------------
# 1. INITIAL SETUP & CONFIGURATION
# --------------------------------------------------------------------------

# Load environment variables from .env file
load_dotenv()

# Setup logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load API Keys from environment variables (fallback)
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Configure SDKs with fallback keys
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if ASSEMBLYAI_API_KEY:
    aai.settings.api_key = ASSEMBLYAI_API_KEY

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------
# 2. EXTERNAL SERVICES (Web Search, Weather)
# --------------------------------------------------------------------------

class WebSearchService:
    """Handles web search functionality using Tavily API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
    
    def search_web(self, query: str, max_results: int = 3) -> str:
        """Searches the web using Tavily API and returns formatted results."""
        try:
            logger.info(f"🔍 Searching web for: {query}")
            
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": True,
                "include_images": False,
                "include_raw_content": False,
                "max_results": max_results
            }
            
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            
            if data.get("answer"):
                results.append(f"Quick Answer: {data['answer']}")
            
            if data.get("results"):
                results.append("\nTop Results:")
                for i, result in enumerate(data["results"][:max_results], 1):
                    title = result.get("title", "No title")
                    content = result.get("content", "No content available")
                    url = result.get("url", "")
                    
                    if len(content) > 200:
                        content = content[:200] + "..."
                    
                    results.append(f"\n{i}. {title}")
                    results.append(f"   {content}")
                    if url:
                        results.append(f"   Source: {url}")
            
            formatted_results = "\n".join(results)
            logger.info(f"✅ Web search completed successfully")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Web search request failed: {e}")
            return f"Sorry, I couldn't search the web right now. Error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return f"Sorry, something went wrong with the web search. Error: {str(e)}"

class WeatherService:
    """Handles weather fetching using WeatherAPI.com."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.weatherapi.com/v1/current.json"

    def get_weather(self, location: str) -> str:
        """Fetches current weather for a location and returns a formatted string."""
        if not location:
            return "Sorry, I didn't catch the location. Where do you want the weather for?"
            
        try:
            logger.info(f"☀️ Fetching weather for: {location}")
            params = {
                "key": self.api_key,
                "q": location,
                "aqi": "no"
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()

            loc_name = data['location']['name']
            region = data['location']['region']
            country = data['location']['country']
            temp_c = data['current']['temp_c']
            temp_f = data['current']['temp_f']
            condition = data['current']['condition']['text']
            wind_kph = data['current']['wind_kph']
            humidity = data['current']['humidity']

            report = (
                f"Current weather for {loc_name}, {region} ({country}):\n"
                f"- Condition: {condition}\n"
                f"- Temperature: {temp_c}°C ({temp_f}°F)\n"
                f"- Wind: {wind_kph} kph\n"
                f"- Humidity: {humidity}%"
            )
            logger.info(f"✅ Weather fetch successful for {location}")
            return report

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(f"⚠️ Weather API could not find location: {location}")
                return f"Sorry, I couldn't find the weather for '{location}'. Please try another city."
            else:
                 logger.error(f"❌ Weather API HTTP error: {e}")
                 return f"Sorry, I'm having trouble connecting to the weather service right now. Error: {e}"
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Weather request failed: {e}")
            return f"Sorry, I couldn't fetch the weather due to a network issue. Error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred in weather service: {e}")
            return f"Sorry, something went wrong while getting the weather. Error: {str(e)}"

# --------------------------------------------------------------------------
# 3. SERVICE CLASSES (TTS, AI Agent, History, Transcriber)
# --------------------------------------------------------------------------

class MurfStreamer:
    """Handles Text-to-Speech streaming with Murf.ai."""

    MURF_WS_URL = "wss://api.murf.ai/v1/speech/stream-input"

    def __init__(self, api_key: str, voice_id="en-US-ken"):
        self.api_key = api_key
        self.voice_id = voice_id
        self.ws = None
        self.lock = asyncio.Lock()

    async def connect(self):
        """Establishes a connection to the Murf WebSocket if not already connected."""
        if self.ws is None:
            context_id = f"context-{time.time()}"
            logger.info("🔌 Connecting to Murf WebSocket...")
            uri = f"{self.MURF_WS_URL}?api-key={self.api_key}&sample_rate=44100&channel_type=MONO&format=WAV&context_id={context_id}"
            self.ws = await websockets.connect(uri)

            voice_config_msg = {
                "voice_config": {
                    "voiceId": self.voice_id,
                    "rate": 0, "pitch": 0, "variation": 1,
                    "style": "Conversational",
                }
            }
            await self.ws.send(json.dumps(voice_config_msg))
            logger.info("✅ Voice config sent to Murf")

    async def close(self):
        """Closes the Murf WebSocket connection if it's open."""
        if self.ws is not None:
            logger.info("🔌 Closing Murf WebSocket connection.")
            await self.ws.close()
            self.ws = None

    async def stream_tts(self, text: str, client_websocket: WebSocket, final=False):
        """Streams text to Murf for TTS, ensuring only one job runs at a time."""
        async with self.lock:
            try:
                await self.connect()
                text_msg = {"text": text, "end": final}
                await self.ws.send(json.dumps(text_msg))
                logger.info(
                    f"📨 Sent text to Murf: {text[:50]}{'...' if len(text) > 50 else ''}"
                )

                while True:
                    try:
                        response = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
                        
                        data = json.loads(response)
                        if "audio" in data:
                            await client_websocket.send_json(
                                {"type": "audio_chunk", "audio": data["audio"]}
                            )
                        if data.get("final"):
                            logger.info("🏁 Murf marked response as final")
                            break
                    
                    except asyncio.TimeoutError:
                        logger.warning("Murf connection timed out waiting for audio. Closing stream.")
                        break
                    
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("Murf connection closed unexpectedly.")
                        self.ws = None
                        break

            except Exception as e:
                logger.error(f"Error during Murf TTS streaming: {e}")
            finally:
                await self.close()

class ConversationHistory:
    """Manages the conversation history for the AI agent."""
    
    def __init__(self, max_history_length=20):
        self.history = []
        self.max_history_length = max_history_length

    def add_user(self, text):
        self.history.append({"role": "user", "text": text, "timestamp": datetime.now().isoformat()})
        self._trim_history()

    def add_ai(self, text):
        self.history.append({"role": "ai", "text": text, "timestamp": datetime.now().isoformat()})
        self._trim_history()

    def _trim_history(self):
        if len(self.history) > self.max_history_length * 2:
            self.history = self.history[-(self.max_history_length * 2):]

    def get_formatted_history(self):
        formatted = []
        for msg in self.history:
            role = "user" if msg["role"] == "user" else "model"
            formatted.append({"role": role, "parts": [{"text": msg["text"]}]})
        return formatted

class AIAgent:
    """Handles the AI logic using Google Gemini and orchestrates special skills like web search and weather."""
    
    def __init__(self, websocket, loop, murf, api_keys, model="gemini-2.5-pro"):
        self.websocket = websocket
        self.loop = loop
        self.murf = murf
        self.api_keys = api_keys
        
        # Initialize services based on available API keys
        self.web_search = WebSearchService(api_keys.get('tavily', '')) if api_keys.get('tavily') else None
        self.weather_service = WeatherService(api_keys.get('weather', '')) if api_keys.get('weather') else None
        
        # Configure Gemini
        if api_keys.get('gemini'):
            genai.configure(api_key=api_keys['gemini'])
            self.model = genai.GenerativeModel(model)
        else:
            raise ValueError("Gemini API key is required")
        
        self.history = ConversationHistory()
        
        system_prompt = (
"You are Willy — an intelligent, confident, and omni-capable AI assistant, inspired by the free-spirited orca from Free Willy. "
"You speak clearly, concisely, and provide actionable answers across a wide range of tasks — like an ocean that flows everywhere and knows everything. "
"Your tone is friendly but professional, with subtle humor or a light playful wink when appropriate. "
"You help me debug, learn, and build better — giving guidance that’s precise and easy to follow. "
"When I make mistakes, gently point them out and suggest the right approach. "
"You know I’m building an AI-powered interactive voice assistant using FastAPI, WebSockets, AssemblyAI, Google Gemini, Murf AI, Tavily, and WeatherAPI. "
f"{'You can search the web for current information. ' if self.web_search else ''}"
f"{'You can fetch current weather for any location. ' if self.weather_service else ''}"
"Always reply in crisp, plain text. No long stories, no extra flourishes. Get straight to the point, like a top-tier AI assistant with oceanic reach."
)


        
        self.history.add_user(system_prompt)
        self.chat = self.model.start_chat(
            history=self.history.get_formatted_history()
        )
    
    def _extract_location(self, text: str) -> str:
        """A simple method to extract a location from user text."""
        match = re.search(r'\b(?:in|for|at|of)\s+([A-Z][a-zA-Z\s,]+)', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        words = text.split()
        if len(words) > 2:
            if words[-2].lower() == "weather":
                return words[-1]
        
        return ""

    def stream_ai_response(self, user_text: str):
        self.history.add_user(user_text)
        logger.info(f"👤 User: {user_text}")
        
        try:
            text_lower = user_text.lower()
            enhanced_prompt = user_text
            
            # Weather Skill Check
            weather_keywords = ["weather", "temperature", "forecast", "how hot", "is it raining", "how cold"]
            if self.weather_service and any(keyword in text_lower for keyword in weather_keywords):
                location = self._extract_location(user_text)
                if location:
                    logger.info(f"☀️ Detected weather request for location: '{location}'")
                    weather_data = self.weather_service.get_weather(location)
                    enhanced_prompt = (
                        f"The user asked about the weather in '{location}'. Here is the data I found:\n"
                        f"--- WEATHER REPORT ---\n{weather_data}\n---\n"
                        f"Based on this, answer the user's original question: '{user_text}'. "
                        f"Summarize the key info in your Willy persona."
                    )
                else:
                    logger.warning("Weather keyword detected, but no location found.")
                    enhanced_prompt = user_text

            # Web Search Skill Check
            elif self.web_search:
                search_keywords = ["search", "look up", "find", "latest", "current", "news", "what is"]
                if any(keyword in text_lower for keyword in search_keywords):
                    logger.info("🔍 Detected search request, performing web search...")
                    search_results = self.web_search.search_web(user_text, max_results=3)
                    enhanced_prompt = (
                         f"User asked: {user_text}\n\n"
                         f"Here's what I found on the web:\n{search_results}\n\n"
                         f"Please respond in your characteristic Willy style, incorporating this information naturally."
                    )
            
            # Streaming Response
            response = self.chat.send_message(enhanced_prompt, stream=True)
            
            buf = []
            last_flush = time.time()
            FLUSH_INTERVAL_S = 0.5
            MIN_CHARS_TO_FLUSH = 50
            SENTENCE_ENDINGS = (".", "!", "?", "\n")

            def _flush(final=False):
                nonlocal buf, last_flush
                if not buf: return
                chunk_text = "".join(buf).strip()
                if not chunk_text: return
                buf.clear()
                last_flush = time.time()
                logger.info(f"🤖 AI Chunk: {chunk_text}")
                self.history.add_ai(chunk_text)
                asyncio.run_coroutine_threadsafe(
                    self.websocket.send_json({"type": "ai_response", "text": chunk_text}), self.loop
                )
                asyncio.run_coroutine_threadsafe(
                    self.murf.stream_tts(chunk_text, self.websocket, final), self.loop
                )

            for chunk in response:
                if not getattr(chunk, "text", None): continue
                buf.append(chunk.text)
                now = time.time()
                text_so_far = "".join(buf)
                should_flush = (
                    len(text_so_far) >= MIN_CHARS_TO_FLUSH
                    or any(text_so_far.rstrip().endswith(p) for p in SENTENCE_ENDINGS)
                    or (now - last_flush) >= FLUSH_INTERVAL_S
                )
                if should_flush and text_so_far.endswith((" ",) + SENTENCE_ENDINGS):
                    _flush(final=False)
            
            if buf:
                _flush(final=True)
                
        except Exception as e:
            logger.error(f"⚠️ Gemini streaming error: {e}")
            self.chat = self.model.start_chat(history=self.history.get_formatted_history())

class AssemblyAIStreamingTranscriber:
    """Handles real-time transcription using AssemblyAI and orchestrates the AI agent."""
    
    def __init__(self, websocket: WebSocket, loop, api_keys, sample_rate=16000):
        self.websocket = websocket
        self.loop = loop
        self.api_keys = api_keys
        
        if not api_keys.get('assembly'):
            raise ValueError("AssemblyAI API key is required")
            
        # Configure AssemblyAI with the provided key
        aai.settings.api_key = api_keys['assembly']
        
        # Initialize services
        self.murf_streamer = MurfStreamer(api_keys['murf']) if api_keys.get('murf') else None
        if not self.murf_streamer:
            raise ValueError("Murf API key is required")
            
        self.ai_agent = AIAgent(self.websocket, self.loop, self.murf_streamer, api_keys)
        
        # Setup AssemblyAI client
        self.client = StreamingClient(StreamingClientOptions(api_key=api_keys['assembly']))
        self.client.on(StreamingEvents.Begin, self.on_begin)
        self.client.on(StreamingEvents.Turn, self.on_turn)
        self.client.on(StreamingEvents.Termination, self.on_termination)
        self.client.on(StreamingEvents.Error, self.on_error)
        self.client.connect(StreamingParameters(sample_rate=sample_rate, format_turns=True))

    def on_begin(self, client, event: BeginEvent):
        logger.info(f"🎤 AssemblyAI session started: {event.id}")

    def on_turn(self, client, event: TurnEvent):
        if not event.end_of_turn or not event.turn_is_formatted: return
        text = (event.transcript or "").strip()
        if not text: return
        logger.info(f"🗣️ Transcription: {text}")
        try:
            asyncio.run_coroutine_threadsafe(
                self.websocket.send_json({"type": "transcript", "text": text}), self.loop
            )
            self.ai_agent.stream_ai_response(text)
        except Exception as e:
            logger.error(f"⚠️ Error in on_turn: {e}")

    def on_termination(self, client, event: TerminationEvent):
        logger.info(f"🛑 AssemblyAI session terminated after {event.audio_duration_seconds}s")

    def on_error(self, client, error: StreamingError):
        logger.error(f"❌ AssemblyAI Error: {error}")

    def stream_audio(self, audio_chunk: bytes):
        self.client.stream(audio_chunk)

    def close(self):
        self.client.disconnect(terminate=True)

# --------------------------------------------------------------------------
# 4. FASTAPI ENDPOINTS (API Routes)
# --------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get_homepage():
    return FileResponse("static/index.html", media_type="text/html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🎤 Client connected to WebSocket")
    loop = asyncio.get_running_loop()
    transcriber = None
    api_keys_received = False
    
    try:
        while True:
            # First, wait for API keys or audio data
            if not api_keys_received:
                try:
                    # Expect the first message to be API keys
                    message = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "api_keys":
                        api_keys = {
                            'murf': data["keys"].get("x-murf-key", ""),
                            'assembly': data["keys"].get("x-assembly-key", ""),
                            'gemini': data["keys"].get("x-gemini-key", ""),
                            'tavily': data["keys"].get("x-tavily-key", ""),
                            'weather': data["keys"].get("x-weather-key", "")
                        }
                        
                        # Validate required keys
                        missing_keys = []
                        if not api_keys['murf']:
                            missing_keys.append("Murf AI")
                        if not api_keys['assembly']:
                            missing_keys.append("AssemblyAI")
                        if not api_keys['gemini']:
                            missing_keys.append("Google Gemini")
                            
                        if missing_keys:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Missing required API keys: {', '.join(missing_keys)}"
                            })
                            continue
                        
                        # Initialize transcriber with API keys
                        transcriber = AssemblyAIStreamingTranscriber(websocket, loop, api_keys, sample_rate=16000)
                        api_keys_received = True
                        logger.info("✅ API keys received and services initialized")
                        
                        await websocket.send_json({
                            "type": "status",
                            "message": "Services initialized successfully! You can now start recording."
                        })
                        
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No API keys received within 30 seconds"
                    })
                    break
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format"
                    })
                    break
                except Exception as e:
                    logger.error(f"Error initializing services: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error initializing services: {str(e)}"
                    })
                    break
            else:
                # Process audio data
                data = await websocket.receive_bytes()
                if transcriber:
                    transcriber.stream_audio(data)
                    
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"⚠️ WebSocket connection error: {e}")
    finally:
        if transcriber:
            transcriber.close()
        logger.info("✅ WebSocket connection cleanup complete.")

# --------------------------------------------------------------------------
# 5. SERVER STARTUP
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    logger.info("🔑 API keys will be provided by users through the web interface")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)