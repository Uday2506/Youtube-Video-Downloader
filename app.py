from flask import Flask, render_template, request, jsonify, send_from_directory
from youtube_downloader import YOUTUBE_ROOT, download_url

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/download", methods=["POST"])
def api_download():
    data = request.get_json(silent=True) or request.form
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify(success=False, error="Please enter a valid YouTube video or playlist URL."), 400

    try:
        download_url(url)
        message = f"Download complete. Files are saved to: {YOUTUBE_ROOT}"
        return jsonify(success=True, message=message)
    except Exception as exc:
        return jsonify(success=False, error=str(exc)), 500

@app.route("/downloads")
def downloads():
    files = []
    for path in sorted(YOUTUBE_ROOT.rglob("*")):
        if path.is_file():
            files.append({
                "name": path.relative_to(YOUTUBE_ROOT).as_posix(),
                "url": f"/downloads/{path.relative_to(YOUTUBE_ROOT).as_posix()}"
            })
    return render_template("downloads.html", files=files)

@app.route("/downloads/<path:filename>")
def download_file(filename: str):
    return send_from_directory(str(YOUTUBE_ROOT), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
