# YouTube Downloader

A beginner-friendly Python project for downloading YouTube videos or full playlists at the highest available quality using `yt-dlp`.

## What this project does

- Downloads single YouTube videos or full playlists
- Always uses the highest available quality
- Uses best video and best audio, then merges into a single MP4 file
- Saves files directly to `C:\Users\<your-username>\Youtube`
- Creates a playlist subfolder and numbers videos in playlist order
- Checks required packages and `ffmpeg` before running

## Folder structure

- `youtube_downloader.py` - main downloader script
- `requirements.txt` - Python dependency list
- `README.md` - project instructions
- `.vscode/tasks.json` - VS Code run task
- `.github/copilot-instructions.md` - workspace Copilot instructions

## Setup instructions for Windows

1. Open this folder in VS Code.
2. Make sure Python 3.8 or newer is installed.
3. In VS Code, select the Python interpreter for your environment.
4. Open a terminal in VS Code.
5. Run:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. The script will also attempt to verify `ffmpeg`.

## Run instructions

1. Open `youtube_downloader.py` in VS Code.
2. Run the script from the terminal:

   ```powershell
   python youtube_downloader.py
   ```

3. When prompted, paste a YouTube video or playlist URL.
4. Wait while the downloader saves the file(s) to your `Youtube` folder.

## VS Code task

Use the task to run the script quickly:

- Open the Command Palette and select `Tasks: Run Task`
- Choose `Run YouTube Downloader`

## Troubleshooting

### `ffmpeg` missing

- The script checks whether `ffmpeg` is available on your PATH.
- If it cannot find it automatically, install `ffmpeg` on Windows and add it to your PATH.
- After installing, restart VS Code or the terminal.

### Invalid URL

- Confirm the pasted URL is a valid YouTube video or playlist link.
- Example video URL: `https://www.youtube.com/watch?v=...`
- Example playlist URL: `https://www.youtube.com/playlist?list=...`

### Video or playlist unavailable

- The video or playlist may have been removed, set to private, or blocked.
- Only download content you own or have permission to download.

### Network errors

- Check your internet connection.
- Retry if the download fails due to a temporary issue.

### `yt-dlp` installation problems

- If auto-install fails, run:

  ```powershell
  python -m pip install -r requirements.txt
  ```

- If the package is still missing, verify your Python interpreter and PATH.

## Notes

- This project does not use third-party download websites.
- It does not bypass DRM, paywalls, login restrictions, age restrictions, or copyright protections.
- Use this only for videos you own, have permission to download, or are legally allowed to download.

