# YouTube Downloader - Render Deployment

A fully working YouTube downloader website hosted on Render using FastAPI, yt-dlp, and ffmpeg.

## Features

- Download single YouTube videos or full playlists
- Highest available quality MP4 output
- Audio-only mode (MP3)
- Real-time progress tracking
- Temporary downloadable links
- Automatic file cleanup (1 hour)
- Graceful error handling for invalid/private videos
- Responsive HTML/CSS/JS frontend
- Docker containerized for Render

## Project Structure

```
.
├── frontend/
│   └── index.html          # Main website UI
├── backend/
│   └── main.py             # FastAPI backend
├── Dockerfile              # Docker build instructions
├── .dockerignore           # Docker ignore file
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
└── README.md               # This file
```

## Local Development

### Prerequisites

- Docker installed
- Git

### Run Locally

1. Clone this repo:
   ```bash
   git clone <your-repo-url>
   cd youtube-downloader
   ```

2. Build and run with Docker:
   ```bash
   docker build -t yt-downloader .
   docker run -p 8000:8000 yt-downloader
   ```

3. Open browser to `http://localhost:8000`

## Deploy to Render

### Step 1: Prepare GitHub Repository

1. Create a new GitHub repository
2. Push this code to the repo:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/youtube-downloader.git
   git push -u origin main
   ```

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: youtube-downloader (or your choice)
   - **Runtime**: Docker
   - **Region**: Any (e.g., Oregon)
   - **Plan**: Free
   - **Dockerfile Path**: `./Dockerfile` (should auto-detect)
   - **Environment Variables**:
     - `PORT`: `8000`
5. Click "Create Web Service"

### Step 3: Deploy

1. Render will automatically build and deploy your Docker container
2. Wait for the build to complete (may take 5-10 minutes)
3. Once deployed, you'll get a public URL like `https://youtube-downloader.onrender.com`

### Step 4: Test

1. Open the public URL in your browser
2. Paste a YouTube URL and click "Download"
3. Monitor real progress
4. Download the file when complete

## Render Free Tier Limitations

- **Cold Starts**: First request after inactivity may take 30-60 seconds
- **Storage**: Files are temporary (auto-deleted after 1 hour)
- **CPU/RAM**: Limited resources, may timeout on large downloads
- **Requests**: Rate limited, avoid rapid successive downloads

## API Endpoints

- `POST /download` - Start download, returns `task_id`
- `GET /status/{task_id}` - Get download progress
- `GET /files/{filename}` - Download completed file
- `GET /` - Serve frontend

## Troubleshooting

### Build Fails
- Check Docker logs in Render dashboard
- Ensure all files are committed to Git

### Downloads Fail
- Check if URL is valid YouTube link
- Private/restricted videos won't work
- Large files may timeout on free tier

### CORS Issues
- Frontend and backend are served from same domain on Render

## Security Notes

- No authentication required
- Files auto-delete after 1 hour
- Basic rate limiting via task tracking
- Only processes YouTube URLs

## License

MIT License