
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

```
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
```

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

## ✅ Day 1: Project Setup – Complete Breakdown

### 🎯 My Task  
Initialize a Python backend using FastAPI. Create a basic `index.html` file and a corresponding JavaScript file for the frontend. Serve the HTML page from your Python server.

---

## 🧠 What I Did (Step-by-Step)

### 🔧 1. FastAPI Backend Setup

You created a file called `main.py` inside a `backend/` folder.  
You imported `FastAPI`, `StaticFiles`, and `Jinja2Templates` to:

- Serve static files (like CSS/JS)
- Render HTML templates using Jinja2

You defined a root route (`/`) that renders `index.html`.

```python
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

✅ This successfully serves the frontend page when you visit:
👉 http://127.0.0.1:8000

🗂 2. Folder Structure

<pre><code>📁 voice-agent/ 
    ├── 📁 backend/ 
    │ └── main.py 
    ├── 📁 static/ 
    │ └── (your CSS and JS are inline for now) 
    ├── 📁 templates/ 
    │ └── index.html </code></pre>

🌐 3. Frontend HTML + CSS + JS
You created an interactive, animated Orca Assistant UI in index.html, using:

### 🌐 Frontend Technologies Used

| Technology         | Purpose                                  |
|--------------------|-------------------------------------------|
| HTML5              | Structure of the web page                 |
| Inline CSS         | Layout, animations, and visual styling    |
| Inline JavaScript  | Adding interactivity and dynamic behavior |


### ✅ Features Implemented

| Feature               | Description                                      |
|-----------------------|--------------------------------------------------|
| 🌌 Gradient Background | Radial ocean theme for immersive atmosphere      |
| 🐳 Orca Animation       | Orca avatar built using pure CSS shapes          |
| 👀 Eye Tracking         | Orca’s eyes follow your mouse movement           |
| ✨ Glowing Pulse        | Orca avatar glows softly at timed intervals      |
| 🎤 Click Response       | Clicking the Orca shows a friendly chat message  |
| 🫧 Bubble Effects       | Floating bubbles add underwater realism          |

📦 4. Static Files Setup
Even though your CSS and JS are inline right now, your FastAPI setup is already ready to serve external CSS and JS files from /static.

 - 📝 LinkedIn Post for Day 1:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_python-30daysofvoiceagents-fastapi-activity-7357460614165778433-Lv7i?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

## ✅ Day 2: Your First REST TTS Call

📌 **Goal**: Create a backend endpoint to generate audio from text using Murf’s TTS REST API.

🔧 **What I did**:
  - Created a new **POST** endpoint in FastAPI `/generate_audio` to accept input text.
  - Integrated Murf.ai’s REST API to convert the text into speech.
  - Returned the audio URL in the JSON response.
  - 
  📸 **How to test**:
  - Used Swagger UI at `localhost:8000/docs` to call the endpoint and preview the response.
  - No frontend changes made on this day.
    
  🛠️ **Tools Used**: FastAPI, Murf API, Python

  - 📝 LinkedIn Post for Day 2: [https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-buildwithmurf-murfai-activity-7357995009343721472-NmV0?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

## ✅ Day 3: Playing Back TTS Audio on UI

📌 **Goal**: Build the frontend to play generated speech.

🔧 **What I did**:
  - Added a text input field and a "Speak" button to the HTML page.
  - On clicking the button, it sends a request to `/generate_audio` with the text input.
  - Used JavaScript to retrieve the audio URL and play it via an `<audio>` element.
  🎯 **Learning Outcome**:
  - Learned to make async fetch calls to the backend and dynamically update the audio player on the page.
  🛠️ **Tools Used**: HTML, JavaScript, FastAPI

  - 📝 LinkedIn Post for Day 3: [https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-fastapi-python-activity-7358077941785767936-Np9D?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

## ✅ Day 4: Echo Bot using MediaRecorder API

📌 **Goal**: Record user’s voice and play it back (Echo Bot).

🔧 **What I did**:
  - Added a new `<h1>` titled **"Echo Bot"** to the existing webpage.
  - Used the browser’s **MediaRecorder API** to:
    - Start recording on "Start Recording" button click.
    - Stop recording on "Stop Recording" button click.
  - Stored the recorded blob and played it back using another `<audio>` element.
    
🎯 **Learning Outcome**:
- Explored browser audio APIs and understood how to handle user media streams.
- 💡 **No Backend Changes** were required for this task.
- 🛠️ **Tools Used**: HTML, JavaScript, MediaRecorder API

- 📝 LinkedIn Post for Day 4: [https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-murfai-voicetech-activity-7358448732624863232-6sn8?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

  ---

## 📁 Folder Structure (updated)

```
voice-agent/
├── backend/
│   └── main.py
├── static/
│   ├── script.js
│   ├── styles.css
│   └── index.html  ← Updated UI for Day 3 and Day 4
├── .env            ← Added to .gitignore
├── .gitignore      ← Added for pyc and env files
```
---
## 🚀 Day 5: Voice Recorder Upload with FastAPI

Today, I took the Echo Bot from Day 4 to the next level by adding **server-side audio upload**! 🎙️⚡

Once you stop recording your voice, it now:
✅ Uploads the audio file to a FastAPI backend  
✅ Displays the file's name, size, and content type on the frontend  
✅ Saves the audio in a dedicated `/uploads` folder on the server

### 🔧 What I Built:
- Auto-upload using JavaScript `fetch` and `FormData`
- Backend endpoint (`/upload/`) using FastAPI to:
  - Receive and save the file
  - Return metadata like filename, content type, and size
- Clear status updates in the browser: "Uploading..." → "✅ Uploaded: filename (size, type)"

### 🧠 What I Learned:
- Using `UploadFile` and `shutil` to handle file uploads in FastAPI
- Showing real-time status to users with dynamic DOM updates
- Structuring backend/frontend cleanly for small web apps

-📝 LinkedIn Post for Day 5:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-murfai-fastapi-activity-7358831843317596161--NuA?utm_source=share&utm_medium=member_android&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 🚀 Day 6: Server-Side Transcription with AssemblyAI

Today, my Voice Agent got a lot smarter — it can now **transcribe spoken words to text** using the power of **AI transcription APIs**!

## 🔧 How it works:

Once I stop recording:

🔁 The bot automatically uploads the audio  
🧠 Sends it to the `/transcribe/file` endpoint on my FastAPI server  
📝 Receives a real-time transcription and displays it in the UI!

## 💡 What I learned:

🔹 Worked with **AssemblyAI SDK** to transcribe in-memory audio bytes  
🔹 Created a new **`/transcribe/file`** endpoint to process audio without saving it  
🔹 Understood how to connect **frontend voice input → backend processing → real-time text output**

🎯 Watching my speech turn into accurate text in seconds felt magical! ✨

## 📚 Resources I used:

- [AssemblyAI Python SDK Docs](https://docs.assemblyai.com/)
- [Voice Agent Series Inspiration](https://lnkd.in/e2Yg6mie)

- 📝 LinkedIn Post for Day 6:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-murfai-assemblyai-activity-7359139467523227648-xoHP?utm_source=share&utm_medium=member_android&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 🚀Day 7: Echo Bot v2
For Day 7, the Echo Bot is upgraded to **repeat back what you said in a Murf AI voice** instead of simply replaying the recorded audio.

### Key Features:
- Records audio from the user
- Sends the audio to the backend `/tts/echo` endpoint
- Uses AssemblyAI to transcribe the audio into text
- Sends the transcription text to Murf API to generate natural-sounding speech
- Returns the Murf-generated audio URL
- Plays the Murf audio in the `<audio>` element on the frontend

You can choose **any voice available** from the Murf API for speech synthesis.

## Endpoint

- **`POST /tts/echo`**  
  Accepts audio file input, transcribes it, generates Murf voice audio, and returns the audio URL.

## How to Use

1. Record your voice in the frontend UI.
2. The audio is sent to the backend `/tts/echo` endpoint.
3. Backend processes transcription and speech synthesis.
4. The Murf audio URL is returned and played back in the UI.

## Resources

- [FastAPI File Upload Tutorial](https://fastapi.tiangolo.com/tutorial/request-files/)
- [AssemblyAI Python SDK Examples](https://github.com/AssemblyAI/assemblyai-python-sdk?tab=readme-ov-file#core-examples)
- [Murf Text-to-Speech API Overview](https://murf.ai/api/docs/text-to-speech/overview)
- [Murf TTS API Reference](https://murf.ai/api/docs/api-reference/text-to-speech/generate)

- 📝 LinkedIn Post for Day 7:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7359525760933486592-gnBw?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 8 - My Voice Agent Just Got a Brain Transplant! 🧠⚡

Up until now, my voice agent could listen 🎧 and talk 🗣️ — but today… it can THINK.

I integrated **Google’s Gemini LLM API** into the backend, giving my agent real intelligence for conversations, Q&A, storytelling, and more!

## 💡 What’s New Today
- 🔹 Built a `POST /llm/query` endpoint in my Python server.
- 🔹 Accepts any text input → sends it to Gemini → returns a smart, human-like reply.
- 🔹 No UI changes needed — just pure backend magic.
- 🔹 Now ready for AI tutors, story generators, research bots, and beyond!

## 📒 Resources Used
- [Google Generative AI Python Client](https://lnkd.in/gsDsPe75)
- [Gemini API Docs](https://lnkd.in/g2RtkDwc)


- 📝 LinkedIn Post for Day 8:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7359856944498528256-wzIx?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 9 - Orca AI Assistant - Live Interaction 🐋👀

Today my voice agent got a *face*… and it’s watching you!  
I built a **playful animated Orca AI Assistant** with **eye tracking** and **live responses**.

## 💡 What’s New Today
- 🎙️ Integrated voice recording & real-time playback with the backend.
- 💬 Now my AI feels *alive* while responding — not just a text box anymore!
- ✨ Fun, interactive experience ready for demos and user engagement.

## 📂 Features
- HTML/CSS Orca assistant UI  
- Voice recording → backend processing → playback  
- Works with my AI backend for smart replies

📝 LinkedIn Post for Day 9: [https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7360232334647873536-a-I_?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 10 | My AI Voice Agent Now Remembers Conversations! 🧠🎙️

## 🚀 Overview
Today’s milestone brings **memory** to my AI Voice Assistant!  
By introducing **chat history with session IDs**, the assistant now engages in **natural, context-aware conversations** — just like talking to a real person.


## ✨ Features
- **Chat History Memory** 🗂️  
  Stores all previous messages in a session for continuity.

- **Multi-Turn Conversations** 💬  
  The assistant remembers past messages, making responses more relevant.

- **Automatic Workflow** ⚡  
  1. Stores conversation history  
  2. Transcribes new audio inputs  
  3. Sends the **full conversation** to the LLM  
  4. Gets a response  
  5. Converts it to speech (TTS)  
  6. Plays it back automatically

- **Seamless UI Flow** 🎨  
  - Saves `session_id` in the browser  
  - Automatically starts recording right after the assistant speaks  
  - Smooth back-and-forth interaction without clicks

-📝 LinkedIn Post for Day 10:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7360725367713640450-4MAv?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 🚀 Day 11 | Building a Resilient AI Voice Agent 🛡️🎙️

## 📌 Overview
Have you ever wondered what happens to an AI voice agent when one of its **core services** unexpectedly fails?  
A crash? Silent failure? Bad user experience?  

Today’s milestone focuses on **resilience** — ensuring that even when key APIs fail, the AI voice agent continues to deliver a smooth and user-friendly experience.

---

## ✨ Key Improvements
### 💠 Robust Error Handling
I implemented **graceful failure management** for a multi-API voice agent.  
The system can now handle failures in:
- **Speech-to-Text (STT)** API
- **Large Language Model (LLM)** API
- **Text-to-Speech (TTS)** API

### 💠 Failure Simulation
To test resilience, I deliberately simulated failures by **commenting out the `GEMINI_API_KEY` and `ASSEMBLYAI_API_KEY`**.

---

## 🔍 What Happens During a Failure?
### **Server-Side**
- **Error Capture:** A `try...except` block catches the failure.
- **Structured Response:** Instead of a generic `500 Internal Server Error`, the server returns:
  ```json
  {
    "error": "Missing GEMINI_API_KEY, ASSEMBLYAI_API_KEY",
    "fallback_audio_url": "https://example.com/fallback.mp3"
  }
-📝 LinkedIn Post for Day 11:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7360969484439859200-3FXz?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# ✨ Day 12 | Revamping the UI 🎨🎙️

## 📌 Overview
Today’s focus was on **UI transformation** for the conversational voice assistant — making it **simpler, smarter, and more user-friendly**.

## ✨ Key Changes
### 🗑️ Removed Unnecessary Sections
- Removed the **initial text-to-speech** and **echo bot** sections to keep the interface focused on the **core voice assistant**.

### 🎛️ Unified Recording Control
- Merged **"Start Recording"** and **"Stop Recording"** into a **single dynamic button**.
- Button now **changes appearance** based on recording status.
- **Auto-play** for audio responses — no more extra clicks to hear the assistant.

### 🎨 Visual Enhancements
- **Prominent mic button** with glowing effect on interaction.
- **Clean, centered layout** for both the agent and chat area.
- **Subtle animations** to make the interface feel more alive and engaging.

-📝 LinkedIn Post for Day 12:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7361353928556376064-3h3-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 📄 Day 13 | Focus: Project Documentation 

Today, I created a **comprehensive `README.md`** for my **AI Voice Agent** project.

## ✅ What the Documentation Covers
- **Project overview & features**
- **Tech stack & architecture**
- **Step-by-step setup instructions**
- **Required environment variables**
- **Screenshots for better clarity**

## 🖋 Why Documentation Matters
Good documentation isn’t just a formality — it’s a **roadmap** for anyone using or contributing to your project.

It helps you:
- 🛠 Onboard new developers faster
- 📦 Ensure reproducibility of setup
- 🔍 Make the project easier to debug & maintain
- 🌍 Reach a wider audience (open-source friendly!)

A well-documented project is like a **product with clear instructions** — people can start using it immediately without guesswork.

-📝 LinkedIn Post for Day 13:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7361814479170408448-YX4X?utm_source=share&utm_medium=member_android&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 📅 Day 14 | Refactoring and Code Cleanup ✍

## 💠 Overview
Today was all about **refactoring**, **cleaning up**, and setting a solid foundation for future development.  
I took the working prototype and transformed it into a more **structured**, **readable**, and **maintainable** project.

## ✅ What I Accomplished Today

### 1. Modular Architecture
Restructured the backend by moving:
- **API endpoints** → `routes/`
- **Business logic** → `services/`
- **Data models** → `schemas/`

This modular approach makes the codebase much cleaner and easier to navigate.

### 2. Improved Maintainability
- Centralized all configurations and API keys into a **`config.py`** file for easier management.

### 3. Code Hygiene
- Removed unused variables and imports.
- Added **better logging** for clearer debugging and monitoring.

### 4. GitHub Ready
- Uploaded the **entire project** to a public GitHub repository.
- Added the **README.md** from yesterday to provide clear setup and usage instructions.


## 💡 Reflection
A **clean, well-organized codebase** is the difference between a quick prototype and a **long-term, scalable project**.  
It’s a **roadmap for collaboration** and a testament to good development practices.

-📝 LinkedIn Post for Day 14:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7362101312450150400-lV2M?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# 🚀 Day 15 | WebSockets in Action 🌐

We’ve officially hit the **halfway mark** of my *30 Days of AI Voice Agents* challenge — and today was all about **real-time communication**. 🎉  

## 💠 Today’s Focus: WebSockets
I implemented a **`/ws` WebSocket endpoint** on my FastAPI server. Using Postman, I was able to:  

- ✅ Establish a WebSocket connection  
- ✅ Send messages from the client  
- ✅ Receive echoed responses back from the server in real-time  

## 🛠️ Development Tip
To keep my codebase clean, I followed the tip of creating a **new branch called `streaming`** so that my non-streaming code remains unaffected.  
This small step goes a long way in ensuring maintainability and smoother development. 💡  

## ✨ Why this matters
WebSockets enable **persistent, low-latency communication**, which is critical for building **responsive voice agents** and **interactive AI systems**.  

-📝 LinkedIn Post for Day 15:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7362445172187521024-A5vV?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 16 | Streaming Audio with WebSockets 🎙️

Today, I extended my WebSocket implementation to handle **real-time audio streaming** from the client to the server.  
Instead of batching audio chunks, the client now sends audio data over **WebSockets** at regular intervals — and the **FastAPI** server saves it directly into a file.  

## 💠 Today’s Focus: Audio Streaming
- 🎤 **Client**: Records audio & streams it live over WebSockets  
- 🌐 **Server**: Receives binary audio data & writes it into a `.webm` file  
- ✅ **Verified** that audio is received correctly and stored without data loss  

## ✨ Why this matters
This is the **foundation for real-time speech processing** in voice agents.  

By streaming audio continuously instead of waiting for full uploads, we unlock possibilities like:
- 🎙️ Live transcription  
- ⚡ Instant responses  
- 🤖 Truly interactive AI systems  

-📝 LinkedIn Post for Day 16:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7362846139273895937-vdjU?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 17 | Real-time Voice Transcription 🚀

For **Day 17** of the **#30DaysOfVoiceAgents** challenge, I’ve leveled up my AI assistant by integrating **AssemblyAI’s Python SDK** to handle **streaming audio transcription**.  

Yesterday was about **sending audio to the server via WebSockets**;  
today is about **understanding it in real-time**.  

## 🔑 Key Achievements
- 🔹 **Set up a WebSocket server** to receive continuous audio streams from the client  
- 🔹 Integrated **AssemblyAI’s Python SDK** to transcribe incoming audio live  
- 🔹 Ensured audio conversion to **16kHz, 16-bit, mono PCM** format (required for streaming API)  
- 🔹 Verified that spoken words appear as **text on the server console almost instantly**  

## ✨ Why this matters
This is a **massive step** towards creating a **truly interactive and responsive voice agent**.  
With **real-time transcription**, we unlock:  
- 🎙️ Instant speech-to-text feedback  
- ⚡ Faster response loops  
- 🤖 Natural, conversational AI experiences

-📝 LinkedIn Post for Day 17:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-buildwithmurf-30daysofvoiceagents-activity-7363418209875628034-sONy?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 18 | Turn Detection 🗣️

For **Day 18** of the **#30DaysOfVoiceAgents** challenge, my AI agent became a **better listener**!  
No more clicking the stop button — the agent now uses **automatic Turn Detection** powered by **AssemblyAI’s streaming API**.  

## 🔑 Key Achievements
- 🤖 Implemented **automatic turn detection** to know when I’ve finished speaking  
- 📝 The `"end of turn"` signal now **finalizes the transcript** automatically  
- ⚡ Triggers the AI’s **response instantly** without manual intervention  
- 🎯 Creates a **seamless, hands-free experience** that feels natural and intuitive  

## ✨ Why this matters
Turn detection is the secret ingredient that makes conversations feel **human** rather than robotic.  
It ensures:
- 🗣️ Smooth, flowing dialogue  
- 🚫 No need for extra clicks or interruptions  
- 🔄 More natural back-and-forth with the AI

-📝 LinkedIn Post for Day 18:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_30daysofvoiceagents-buildwithmurf-30daysofvoiceagents-activity-7363525982730792960-VI86?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 19: Streaming LLM Responses

Today's task focused on enhancing user experience by implementing **streaming LLM responses** in a voice assistant project.

## Overview

Instead of waiting for the assistant to generate an entire response, the LLM now streams its output **word-by-word in real-time**. This significantly reduces perceived latency, making the interaction feel faster and more natural.

## How It Works

1. **Capture Audio Transcript**  
   The final user audio is transcribed using **AssemblyAI**.

2. **Send Transcript to LLM**  
   The Python backend (built with **FastAPI**) sends this transcript to **Google's Gemini API** with streaming enabled.

3. **Receive Streaming Response**  
   The server receives the response in **chunks** and prints each chunk to the console immediately as it arrives.

-📝 LinkedIn Post for Day 19:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7363899568645681152-Czrb?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---

# Day 20: Murf WebSockets 🚀

There’s something genuinely exciting about seeing raw data stream into the console.  
Today, I connected the dots in my **AI Voice Agent** project:  

## 🔹 What I Built
- 🎙️ Captured my voice with **AssemblyAI**  
- ✍️ Generated a streaming text response from **Gemini**  
- 🔊 Piped that text, **chunk-by-chunk**, to the **Murf AI TTS WebSocket**  
- 🎧 Received the voice back as a **real-time stream of base64 audio**  
- 🔄 Used a **static `context_id`** to avoid session limit errors and maintain a single streaming context  

## ⚡ Key Learning
This task was a **fantastic exercise in handling asynchronous communication**.  
Building this agent piece by piece has been an **amazing learning journey**.  

👉 On to the final **10 days**!  

## 📚 Resource
- [Murf AI WebSocket Streaming Guide](https://lnkd.in/gtaT3Rxr)

-📝 LinkedIn Post for Day 20:[https://www.linkedin.com/posts/kiruthika-m-66b1a5254_buildwithmurf-30daysofvoiceagents-murfai-activity-7364287244892819456-JWKb?utm_source=share&utm_medium=member_desktop&rcm=ACoAAD6tG3MBYWx9mOEBXuTEYqfqcrMbrpxUBwE]

---




