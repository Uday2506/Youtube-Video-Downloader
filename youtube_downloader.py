import importlib
import shutil
import subprocess
import sys
from pathlib import Path

YOUTUBE_ROOT = Path.home() / "Youtube"
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"


def ensure_directory(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def install_requirements() -> None:
    try:
        importlib.import_module("yt_dlp")
        return
    except ImportError:
        print("Installing required Python packages from requirements.txt...")

    if not REQUIREMENTS_FILE.exists():
        raise FileNotFoundError("requirements.txt not found. Please make sure it exists in the project folder.")

    command = [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError("Failed to install required Python packages. Please run the command manually.")


def find_ffmpeg() -> bool:
    if shutil.which("ffmpeg"):
        return True
    return False


def run_command(command: list[str]) -> bool:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return True
        print(result.stdout)
        print(result.stderr)
    except subprocess.TimeoutExpired:
        print("Installation timed out.")
        return False
    except FileNotFoundError:
        pass
    return False


def get_user_input() -> str:
    print("\nEnter a YouTube video URL or playlist URL.")
    url = input("URL: ").strip()
    if not url:
        raise ValueError("No URL entered. Please enter a valid YouTube URL.")
    return url


def format_error_message(error: str) -> str:
    lowered = error.lower()
    if "unable to download" in lowered or "http error" in lowered:
        return "Network error or connection issue. Check your internet connection and try again."
    if "video unavailable" in lowered or "not available" in lowered:
        return "The requested video is unavailable. It may have been removed or restricted."
    if "playlist" in lowered and "unavailable" in lowered:
        return "The requested playlist is unavailable. Verify the playlist URL and try again."
    if "unsupported url" in lowered or "invalid url" in lowered or "no video id" in lowered:
        return "The URL does not appear to be a valid YouTube video or playlist link."
    return "An error occurred while downloading. Please verify the URL and your network connection."


def download_url(url: str) -> None:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    ensure_directory(YOUTUBE_ROOT)

    ydl_opts = {
        "format": "bestvideo[ext=mp4][vcodec=h264]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": str(YOUTUBE_ROOT / "%(title)s.%(ext)s"),
        "noplaylist": False,
        "ignoreerrors": False,
        "no_warnings": True,
        "quiet": False,
        "writesubtitles": False,
        "retries": 3,
        "playlist_items": None,
    }

    try:
        with YoutubeDL({**ydl_opts, "quiet": True, "ignoreerrors": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as error:
        raise RuntimeError(format_error_message(str(error))) from error
    except Exception as error:
        raise RuntimeError("Could not read the URL. Please check that the link is a valid YouTube video or playlist.") from error

    is_playlist = info.get("_type") == "playlist" or info.get("entries") is not None

    if is_playlist:
        playlist_title = info.get("title") or "playlist"
        playlist_folder = sanitize_filename(playlist_title)
        playlist_dir = YOUTUBE_ROOT / playlist_folder
        ensure_directory(playlist_dir)
        ydl_opts["outtmpl"] = str(playlist_dir / "%(playlist_index)03d - %(title)s.%(ext)s")
        ydl_opts["ignoreerrors"] = True
    else:
        ydl_opts["outtmpl"] = str(YOUTUBE_ROOT / "%(title)s.%(ext)s")
        ydl_opts["noplaylist"] = True

    print(f"\nDownloading to: {YOUTUBE_ROOT}")
    if is_playlist:
        print(f"Playlist detected. Files will be placed in: {playlist_dir}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nDownload complete.")
    except DownloadError as error:
        raise RuntimeError(format_error_message(str(error))) from error
    except Exception as error:
        raise RuntimeError("An unexpected error occurred during download.") from error


def sanitize_filename(value: str) -> str:
    safe = value.replace("<", "").replace(">", "").replace(":", "").replace("\"", "").replace("/", "").replace("\\", "").replace("|", "").replace("?", "").replace("*", "")
    return safe.strip() or "playlist"


def main() -> None:
    try:
        install_requirements()
    except Exception as error:
        print(f"\nFailed to install Python requirements: {error}")
        sys.exit(1)

    if not find_ffmpeg():
        print("\n❌ ffmpeg is required for merging video and audio into MP4.")
        print("\nTo install ffmpeg on Windows:")
        print("\nOption 1 (Easiest - if you have Chocolatey):")
        print("  1. Open PowerShell as Administrator")
        print("  2. Run: choco install ffmpeg")
        print("\nOption 2 (Using winget):")
        print("  1. Open PowerShell as Administrator")
        print("  2. Run: winget install ffmpeg")
        print("\nOption 3 (Manual):")
        print("  1. Download ffmpeg from: https://ffmpeg.org/download.html")
        print("  2. Extract to a folder (e.g., C:\\ffmpeg)")
        print("  3. Add to PATH or restart VS Code after installation")
        print("\nOnce installed, restart VS Code or the terminal and try again.")
        sys.exit(1)

    try:
        url = get_user_input()
        download_url(url)
    except ValueError as error:
        print(f"\nInput error: {error}")
        sys.exit(1)
    except RuntimeError as error:
        print(f"\nError: {error}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
