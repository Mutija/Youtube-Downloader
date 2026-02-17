from flask import Flask, request, send_file, send_from_directory, jsonify
from pytubefix import YouTube
from io import BytesIO

app = Flask(__name__, static_folder="static")


@app.route("/")
def home():
    return send_from_directory("static", "index.html")


@app.route("/download", methods=["POST"])
def download_video():
    data = request.json
    url = data["url"]

    yt = YouTube(url)

    stream = (
        yt.streams
        .filter(only_video=True, res="1080p", fps=60)
        .order_by("resolution")
        .desc()
        .first()
    ) or (
        yt.streams
        .filter(only_video=True, res="1080p")
        .order_by("fps")
        .desc()
        .first()
    ) or (
        yt.streams
        .filter(only_video=True)
        .order_by("resolution")
        .desc()
        .first()
    )

    if stream is None:
        return jsonify({"error": "Nije pronađen video-only stream."}), 400

    ext = "mp4"
    if stream.mime_type and "webm" in stream.mime_type:
        ext = "webm"

    safe_title = "".join(c for c in yt.title if c not in '\\/:*?"<>|')
    filename = f"{safe_title}.{ext}"

    # skini u memoriju
    buffer = BytesIO()
    stream.stream_to_buffer(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype=stream.mime_type or "application/octet-stream",
    )


@app.route("/download-audio", methods=["POST"])
def download_audio():
    data = request.json
    url = data["url"]

    yt = YouTube(url)
    audio_stream = yt.streams.get_audio_only()

    if audio_stream is None:
        return jsonify({"error": "Nije pronađen audio stream."}), 400

    safe_title = "".join(c for c in yt.title if c not in '\\/:*?"<>|')
    filename = f"{safe_title}.mp3"

    buffer = BytesIO()
    audio_stream.stream_to_buffer(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype=audio_stream.mime_type or "audio/mpeg",
    )


if __name__ == "__main__":
    app.run(debug=True)
