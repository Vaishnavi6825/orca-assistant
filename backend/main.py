import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import BASE_DIR, FRONTEND_DIR, UPLOAD_DIR
from .routes import tts_routes, chat_routes

logger = logging.getLogger("uvicorn.error")

# ✅ Create FastAPI app
app = FastAPI(title="AI Voice Agent Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Mount static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
else:
    logger.warning("Static frontend directory not found — skipping /static mount.")

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ✅ Include routers
app.include_router(tts_routes.router, prefix="/api", tags=["TTS & Transcription"])
app.include_router(chat_routes.router, prefix="/api", tags=["Agent Chat"])

# ✅ Serve index.html on root URL
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Frontend not found</h1>")
