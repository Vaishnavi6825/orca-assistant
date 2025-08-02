# 🐳 orca-assistant

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
    ├── 📁 backend/ │ └── main.py 
    ├── 📁 static/ │ └── (your CSS and JS are inline for now) 
    ├── 📁 templates/ │ └── index.html </code></pre>

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


