from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from pytubefix import YouTube
import os
from io import BytesIO

app = Flask(__name__)
CORS(app)  # dopušta pozive s GitHub Pages frontenda

@app.route("/", methods=["GET"])
def index():
    return "YouTube downloader backend radi."

@app.route("/download", methods=["POST"])
def download_video():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Nije poslan URL."}), 400

        yt = YouTube(url)
        stream = yt.streams.filter(progressive=False, file_extension="mp4", res="1080p").first()
        if stream is None:
            # fallback na najbolji mp4 ako nema baš 1080p
            stream = yt.streams.filter(progressive=False, file_extension="mp4").order_by("resolution").desc().first()

        if stream is None:
            return jsonify({"error": "Nije pronađen video stream."}), 404

        buffer = BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        filename = f"{yt.title}.mp4".replace("/", "_")

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download-audio", methods=["POST"])
def download_audio():
    try:
        data = request.get_json()
        url = data.get("url")
        if not url:
            return jsonify({"error": "Nije poslan URL."}), 400

        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        if stream is None:
            return jsonify({"error": "Nije pronađen audio stream."}), 404

        buffer = BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        filename = f"{yt.title}.mp3".replace("/", "_")

        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="audio/mpeg",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # lokalno testiranje
    app.run(host="0.0.0.0", port=5000, debug=True)
