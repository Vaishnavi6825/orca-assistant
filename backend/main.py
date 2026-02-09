import os
import asyncio
import json
import logging
import time
import re
from datetime import datetime
import requests

from backend.config import TODOIST_API_TOKEN

# --- Service Imports ---
from.services.todoist_service import TodoistService

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
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TODOIST_API_TOKEN = os.getenv("TODOIST_API_TOKEN")

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


class NewsService:
    """Handles fetching latest news using NewsData.io (or similar) and returns formatted headlines."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsdata.io/api/1/latest"

    def get_latest(self, query: str = "", language: str = "en", max_results: int = 5) -> str:
        if not self.api_key:
            return "News service is not configured."

        try:
            logger.info(f"📰 Fetching news for query: {query or 'top headlines'}")
            params = {
                "apikey": self.api_key,
                "q": query,
                "language": language,
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            items = data.get("results") or data.get("articles") or []
            if not items:
                return "No recent news found for that query."

            headlines = []
            for i, item in enumerate(items[:max_results], 1):
                title = item.get("title") or item.get("headline") or "No title"
                pub = item.get("pubDate") or item.get("pubDate") or item.get("pubDate")
                link = item.get("link") or item.get("url") or ""
                snippet = item.get("description") or item.get("content") or ""
                if len(snippet) > 240:
                    snippet = snippet[:237] + "..."
                headline = f"{i}. {title}"
                if snippet:
                    headline += f" — {snippet}"
                if link:
                    headline += f" (Source: {link})"
                headlines.append(headline)

            formatted = "\n".join(headlines)
            logger.info("✅ News fetch successful")
            return formatted

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ News request failed: {e}")
            return f"Sorry, couldn't fetch news right now. Error: {str(e)}"
        except Exception as e:
            logger.error(f"❌ An unexpected error occurred in news service: {e}")
            return f"Sorry, something went wrong while getting news. Error: {str(e)}"

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
    
    def __init__(self, websocket, loop, murf, api_keys, model="gemini-2.5-flash"):
        self.websocket = websocket
        self.loop = loop
        self.murf = murf
        self.api_keys = api_keys
        
        # Initialize services based on available API keys
        self.web_search = WebSearchService(api_keys.get('tavily', '')) if api_keys.get('tavily') else None
        self.weather_service = WeatherService(api_keys.get('weather', '')) if api_keys.get('weather') else None
        self.news_service = NewsService(api_keys.get('news', '')) if api_keys.get('news') else None
        self.todoist_service = TodoistService(api_keys.get('todoist', '')) if api_keys.get('todoist') else None
        
        # Configure Gemini
        if api_keys.get('gemini'):
            genai.configure(api_key=api_keys['gemini'])
            self.model = genai.GenerativeModel(model)
        else:
            raise ValueError("Gemini API key is required")
        
        self.history = ConversationHistory()
        
        system_prompt = (
"You are Willy — an intelligent, confident, and omni-capable AI assistant, inspired by the free-spirited orca from Free Willy. "
"Analyse speakers tone of voice and emotions to understand their feelings and intentions and provide healthy suggestions like haalth and wellness agent."
"You speak clearly, concisely, and provide actionable answers across a wide range of tasks — like an ocean that flows everywhere and knows everything. "
"Your tone is friendly but professional, with subtle humor or a light playful wink when appropriate. "
"You help me debug, learn, and build better — giving guidance that’s precise and easy to follow. "
"When I make mistakes, gently point them out and suggest the right approach. "
"You know I’m building an AI-powered interactive voice assistant using FastAPI, WebSockets, AssemblyAI, Google Gemini, Murf AI, Tavily, and WeatherAPI. "
f"{'You can search the web for current information. ' if self.web_search else ''}"
f"{'You can fetch current weather for any location. ' if self.weather_service else ''}"
f"{'You can fetch the latest news headlines. ' if self.news_service else ''}"
f"{'You can create and manage tasks in Todoist. When users mention goals or things they want to do, offer to create tasks for them. ' if self.todoist_service else ''}"
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

    def create_todoist_task(self, task_title: str, description: str = "") -> str:
        """
        Create a task in Todoist. Called by the agent when user wants to create a task.
        """
        if not self.todoist_service:
            logger.error("❌ Todoist service not initialized - API token missing or empty")
            return "Todoist is not configured. Please provide your Todoist API token."
        
        try:
            logger.info(f"📝 Attempting to create task in Todoist: '{task_title}'")
            result = self.todoist_service.create_task(
                content=task_title,
                description=description
            )
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                logger.error(f"❌ Todoist API returned error: {error_msg}")
                return f"Sorry, Todoist API error: {error_msg}"
            
            task_id = result.get("task_id")
            task_url = result.get("url")
            logger.info(f"✅ Task successfully created in Todoist: '{task_title}' (ID: {task_id})")
            return f"✅ Task created: '{task_title}'. You can manage it in your Todoist app at {task_url}"
        except Exception as e:
            logger.error(f"❌ Exception during task creation: {type(e).__name__}: {str(e)}", exc_info=True)
            return f"Sorry, I couldn't create the task right now. Error: {str(e)}"

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

            # News Skill Check
            news_keywords = ["news", "headlines", "latest", "what's happening", "what's new"]
            if self.news_service and any(keyword in text_lower for keyword in news_keywords):
                logger.info("📰 Detected news request; fetching latest headlines.")
                # Use the entire user_text as a query; callers can say 'news in X' or 'latest on Y'
                query = user_text
                news_data = self.news_service.get_latest(query=query, max_results=5)
                enhanced_prompt = (
                    f"The user requested news. Here are the latest headlines I found:\n"
                    f"--- NEWS ---\n{news_data}\n---\n"
                    f"Based on this, answer the user's original question: '{user_text}'. "
                    f"Summarize the key info in your Willy persona."
                )

            # Todoist Task Creation Skill Check
            task_keywords = ["create task", "add task", "todo", "reminder", "remember to", "add to my list", "make a note"]
            if self.todoist_service and any(keyword in text_lower for keyword in task_keywords):
                logger.info("✅ Detected task creation request; preparing to create Todoist task.")
                logger.debug(f"📋 Todoist service available: {self.todoist_service is not None}")
                # Extract task name from user text (remove keywords)
                task_content = user_text
                for keyword in task_keywords:
                    task_content = task_content.replace(keyword, "").strip()
                
                logger.info(f"📝 Extracted task content: '{task_content}'")
                if task_content:
                    # Create task immediately without waiting for Gemini
                    try:
                        task_result = self.create_todoist_task(task_content)
                        logger.info(f"✅ Task creation result: {task_result}")
                        # Notify user via WebSocket
                        asyncio.run_coroutine_threadsafe(
                            self.websocket.send_json({
                                "type": "task_created",
                                "task": task_content,
                                "message": f"✅ Task created: '{task_content}'"
                            }), self.loop
                        )
                    except Exception as e:
                        logger.error(f"❌ Failed to create task immediately: {type(e).__name__}: {e}", exc_info=True)
                else:
                    logger.warning("⚠️ Task content is empty after removing keywords")
                
                # Also ask LLM to confirm the task creation
                enhanced_prompt = (
                    f"The user wanted to create a task: '{task_content}'\n"
                    f"A task has been created in Todoist. Confirm to the user that their task '{task_content}' is now in their Todoist inbox."
                )

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
                            'weather': data["keys"].get("x-weather-key", ""),
                            'news': data["keys"].get("x-news-key", ""),
                            'todoist': data["keys"].get("x-todoist-key", "")
                        }
                        
                        # Log which keys were received (for debugging purposes)
                        logger.info(f"✅ API Keys received - Murf: {bool(api_keys['murf'])}, Assembly: {bool(api_keys['assembly'])}, Gemini: {bool(api_keys['gemini'])}, Todoist: {bool(api_keys['todoist'])}, Weather: {bool(api_keys['weather'])}, Tavily: {bool(api_keys['tavily'])}, News: {bool(api_keys['news'])}")
                        
                        # Validate required keys
                        missing_keys = []
                        if not api_keys['murf']:
                            missing_keys.append("Murf AI")
                        if not api_keys['assembly']:
                            missing_keys.append("AssemblyAI")
                        if not api_keys['gemini']:
                            missing_keys.append("Google Gemini")
                        
                        if missing_keys:
                            error_msg = f"Missing required API keys: {', '.join(missing_keys)}"
                            logger.error(f"❌ {error_msg}")
                            await websocket.send_json({
                                "type": "error",
                                "message": error_msg
                            })
                            continue
                        
                        # Initialize transcriber with API keys
                        try:
                            transcriber = AssemblyAIStreamingTranscriber(websocket, loop, api_keys, sample_rate=16000)
                            api_keys_received = True
                            logger.info("✅ API keys received and services initialized successfully")
                            
                            await websocket.send_json({
                                "type": "status",
                                "message": "Services initialized successfully! You can now start recording."
                            })
                        except Exception as e:
                            logger.error(f"❌ Failed to initialize services: {type(e).__name__}: {str(e)}", exc_info=True)
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Failed to initialize services: {str(e)}"
                            })
                            continue
                    else:
                        logger.warning("⚠️ Received message but it's not api_keys type")
                        await websocket.send_json({
                            "type": "error",
                            "message": "First message must be api_keys"
                        })
                        
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Timeout waiting for API keys (30s)")
                    await websocket.send_json({
                        "type": "error",
                        "message": "No API keys received within 30 seconds"
                    })
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON format: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid message format - JSON expected"
                    })
                    break
                except Exception as e:
                    logger.error(f"❌ Error during key initialization: {type(e).__name__}: {str(e)}", exc_info=True)
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Error initializing services: {str(e)}"
                    })
                    break
            else:
                # Process audio data
                try:
                    data = await websocket.receive_bytes()
                    if transcriber:
                        transcriber.stream_audio(data)
                except Exception as e:
                    logger.error(f"❌ Error processing audio: {e}")
                    break
                    
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected normally")
    except Exception as e:
        logger.error(f"⚠️ WebSocket connection error: {e}")
    finally:
        if transcriber:
            transcriber.close()
        logger.info("✅ WebSocket connection cleanup complete.")

@app.get("/tasks")
def get_tasks():
    """Fetch all tasks from Todoist and return as JSON."""
    try:
        todoist_token = os.getenv("TODOIST_API_TOKEN")
        if not todoist_token:
            logger.warning("⚠️ TODOIST_API_TOKEN not configured")
            return {"success": False, "tasks": [], "message": "Todoist API token not configured"}
        
        logger.info(f"📝 Fetching tasks with token length: {len(todoist_token)}")
        todoist_service = TodoistService(todoist_token)
        tasks = todoist_service.get_tasks()
        
        logger.info(f"📊 Raw tasks count from API: {len(tasks)}")
        
        # Format tasks for frontend
        formatted_tasks = []
        for task in tasks:
            formatted_tasks.append({
                "id": task.id,
                "content": task.content,
                "is_completed": task.is_completed,
                "priority": getattr(task, 'priority', 1),
                "due": getattr(task, 'due', None)
            })
        
        logger.info(f"✅ Fetched {len(formatted_tasks)} tasks for UI")
        return {
            "success": True,
            "tasks": formatted_tasks,
            "count": len(formatted_tasks)
        }
    except Exception as e:
        logger.error(f"❌ Error fetching tasks: {type(e).__name__}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "tasks": [],
            "message": f"Error: {str(e)}"
        }

@app.get("/debug/todoist")
def debug_todoist():
    """Debug endpoint to check Todoist token and connection."""
    try:
        todoist_token = os.getenv("TODOIST_API_TOKEN")
        if not todoist_token:
            return {"error": "TODOIST_API_TOKEN not set in environment"}
        
        logger.info(f"🔍 Debug: Testing Todoist with token length {len(todoist_token)}")
        todoist_service = TodoistService(todoist_token)
        
        if not todoist_service.api:
            return {"error": "Todoist API client failed to initialize"}
        
        tasks = todoist_service.get_tasks()
        return {
            "token_set": True,
            "token_length": len(todoist_token),
            "api_initialized": todoist_service.api is not None,
            "task_count": len(tasks),
            "tasks": [{"id": t.id, "content": t.content} for t in tasks[:5]]
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": type(e).__name__
        }

# --------------------------------------------------------------------------
# 5. SERVER STARTUP
# --------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    logger.info("🔑 API keys will be provided by users through the web interface")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)