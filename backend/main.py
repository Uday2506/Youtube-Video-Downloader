from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import yt_dlp
import os
import uuid
import shutil
from pathlib import Path
import asyncio
import time
from urllib.parse import urlparse

app = FastAPI(title="YouTube Downloader API")

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent.parent

# Serve the frontend UI
frontend_dir = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def read_index():
    index_file = BASE_DIR / "frontend" / "index.html"
    return FileResponse(path=str(index_file), media_type="text/html")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
DOWNLOAD_DIR = Path("/tmp/downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Task storage
tasks = {}

class DownloadRequest(BaseModel):
    url: str
    mode: Optional[str] = "best"

class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    download_url: Optional[str] = None

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()

def cleanup_old_files():
    """Delete files older than 1 hour"""
    now = time.time()
    for file_path in DOWNLOAD_DIR.glob("*"):
        if file_path.is_file() and (now - file_path.stat().st_mtime) > 3600:
            file_path.unlink()

async def download_video(url: str, mode: str, task_id: str):
    tasks[task_id] = {"status": "starting", "progress": 0, "message": "Initializing download...", "download_url": None}

    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")

        # yt-dlp options
        ydl_opts = {
            'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4][vcodec=h264]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'noplaylist': False,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: update_progress(d, task_id)],
        }

        if mode == "audio":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            ydl_opts['outtmpl'] = str(DOWNLOAD_DIR / '%(title)s.%(ext)s')

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            tasks[task_id]["message"] = f"Downloading: {info.get('title', 'Unknown')}"
            ydl.download([url])

        # Find the downloaded file
        files = list(DOWNLOAD_DIR.glob("*"))
        if files:
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            download_url = f"/files/{latest_file.name}"
            tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Download completed",
                "download_url": download_url
            })
        else:
            raise Exception("No file was downloaded")

    except Exception as e:
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": str(e),
            "download_url": None
        })

def update_progress(d, task_id):
    if d['status'] == 'downloading':
        progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        tasks[task_id]["progress"] = min(progress, 99)
        tasks[task_id]["message"] = f"Downloading... {progress:.1f}%"

@app.post("/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(download_video, request.url, request.mode, task_id)
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(**tasks[task_id])

@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = DOWNLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='application/octet-stream')

@app.on_event("startup")
async def startup_event():
    # Cleanup old files on startup
    cleanup_old_files()

@app.middleware("http")
async def cleanup_middleware(request: Request, call_next):
    response = await call_next(request)
    # Cleanup after each request
    cleanup_old_files()
    return response