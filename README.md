# 🐳 orca-assistant
# 🔊 30 Days of AI Voice Agents 

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






