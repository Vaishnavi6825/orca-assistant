
# 🐳 ORCA assistant - AI Voice Agent
# 🔊 30 Days of AI Voice Agents 

An interactive AI-powered voice assistant that listens to your speech, processes it using advanced AI models, and responds with natural-sounding speech.

<img width="1251" height="684" alt="image" src="https://github.com/user-attachments/assets/2c865684-b67f-432f-9069-df3d9b1eb6a2" />


This project integrates multiple advanced AI services and technologies:

- **AssemblyAI** for accurate speech-to-text transcription.
- **Google Gemini (Generative AI)** for intelligent, context-aware responses.
- **Murf AI** for lifelike text-to-speech voice output.
- **FastAPI** for a fast, modern Python backend.
- **Custom JavaScript Frontend** for seamless user interaction and session management.

---

## Features

- 🎙 **Voice Interaction** – Speak naturally and get instant responses.
- 🧠 **AI-Powered Replies** – Uses Google Generative AI for context-aware answers.
- 🗣 **Natural Voice Output** – Converts text replies into human-like speech via Murf AI.
- 🌐 **Web-Based Interface** – Works directly in the browser.
- ⚡ **Real-Time Processing** – Minimal delay between speaking and hearing the reply.

---

## Tech Stack

**Frontend:** HTML, CSS, JavaScript  
**Backend:** Python (FastAPI)  

**APIs:**
- **AssemblyAI** – Speech-to-text transcription  
- **Google Generative AI** – AI-generated responses  
- **Murf AI** – Text-to-speech synthesis  

**Other Libraries:**  
- `requests` – API requests  
- `pydantic` – Data validation  

---

## About the UI Style

The UI is designed to be modern, interactive, and visually engaging:
- **Animated Orca Avatar:** Features glowing effects, eye tracking, and smooth animations.
- **Ocean Theme:** Uses a dark, ocean-inspired background with bubbles and ripple effects.
- **Responsive Design:** Works well on both desktop and mobile browsers.
- **Accessible Controls:** Large microphone button, clear status messages, and chat history for easy use.
- **Live Feedback:** Real-time updates for recording, processing, and bot responses.

---

## How It Works

1. User clicks **Record** → speaks into microphone.  
2. Audio is sent to **AssemblyAI** → returns transcribed text.  
3. Text is sent to **Google Generative AI** → returns AI-generated reply.  
4. Reply is sent to **Murf AI** → generates voice output.  
5. Audio is played in the browser.

---

## API Endpoints

| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| POST   | `/api/agent/chat`   | Send audio and receive voice reply |

---

## Dependencies

- fastapi  
- uvicorn  
- requests  
- python-dotenv  
- pydantic  

Install all at once:
```bash
pip install fastapi uvicorn requests python-dotenv pydantic
```
---

## Project Structure

```
.
├── backend/
│   ├── __pycache__/
│   ├── uploads/
│   └── main.py
├── orca-assistant/
├── static/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── orca-demo.jpg
├── venv/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
```
- `backend/` — FastAPI backend and uploads
- `orca-assistant/` — (your extra folder, if used)
- `static/` — Frontend files (HTML, JS, CSS, images)
- `venv/` — Python virtual environment
- `.env` — Environment variables
- `.gitignore` — Git ignore file
- `README.md` — Documentation
- `requirements.txt` — Python dependencies

---

## Environment Variables

Create a `.env` file in the project root and add:

- *ASSEMBLYAI_API_KEY=your_assemblyai_api_key
- *GEMINI_API_KEY=your_gemini_api_key
- *MURF_API_KEY=your_murf_api_key
- *TAVILY_API_KEY=your_tavily_api_key
- *WEATHER_API_KEY=your_weatherapi_key

---

## Quickstart

1. **Clone the repo and enter the folder:**
    ```bash
    git clone https://github.com/Vaishnavi6825/orca-assistant.git 
    cd orca-assistant
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    # or
    source venv/bin/activate   # On Mac/Linux
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Add your `.env` file as described above.**

5. **Start the server:**
    ```bash
    uvicorn backend.main:app --reload
    ```
6. **Open in your browser:**  
   [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Test the Voice Agent

1. **Start the backend server** (see Quickstart above).
2. **Open the app** in your browser.
3. **Click the microphone button** to record your voice.
4. **Speak your question or command**.
5. **Wait for the Orca Assistant to reply** with both text and voice.

You should see your conversation in the chat history and hear the Orca’s response!

---

## REAL TIME STREAMING THROUGH WEBSOCKETS
## ✨ Key Features

- 🎙 **Voice Interaction** – Speak naturally and get instant AI-powered replies.  
- 🌐 **Streaming WebSockets** – Real-time audio transcription, response streaming, and playback.  
- 🗣 **Natural Voice Output** – Human-like speech via Murf AI streaming TTS.  
- 🧠 **Smarter AI** – Context-aware replies using Google Gemini, with persona (Orca 🐳).  
- 🔍 **Special Skills** – Live web search (Tavily API) and real-time weather (WeatherAPI).  
- 🎨 **Modern UI/UX** – Dark theme, animated Orca avatar, and live feedback notifications.  
- 🔑 **Secure Setup** – User-provided API keys via an interactive modal.  
- 🚀 **Deployed Online** – Accessible on Render.  

---

**APIs:**  
- **AssemblyAI** – Live transcription  
- **Google Gemini** – Generative AI responses  
- **Murf AI** – Streaming TTS voice synthesis  
- **Tavily** – Real-time web search  
- **WeatherAPI** – Live weather data  

---

### 🎤 How to Use

1. Open the app (locally or via Live Demo).
2. Enter your API keys in the configuration modal.
3. Click the 🎙 microphone button and start speaking.

ORCA Assistant will:

Listen → live transcription via AssemblyAI
Think → reply using Gemini + persona
Speak → stream TTS from Murf AI
Act → fetch real-time web or weather info when needed

---

### Demo

🌐 Live Deployment: [https://orca-assistant.onrender.com/?session=b9774b19-9b23-4139-9a68-46e507860741](#)  

---

## Future Improvements

- Add support for multiple voices and languages  
- Improve response latency with streaming transcription + TTS  
- Deploy on cloud (Render / Vercel / AWS)  
- Add authentication and personalization  

---

## Journey & Daily Logs

This project was built as part of **30 Days of AI Voice Agents Challenge** 🗓️.  
All daily progress, learnings, and detailed notes are documented in [JOURNEY.md](./JOURNEY.md).  

---

## Author

👩‍💻 **KIRUTHIKA M** 

- GitHub: [Vaishnavi6825](https://github.com/Vaishnavi6825)  
- LinkedIn: [https://www.linkedin.com/in/kiruthika-m-66b1a5254/](#)  

---







