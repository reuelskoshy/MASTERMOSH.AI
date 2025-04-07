from flask import Flask, request, jsonify, send_file, render_template
import os
import subprocess
import whisper
import requests
from gtts import gTTS
import re
import time
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(minutes=30)

# Configure folders
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
STATIC_FOLDER = os.path.join(os.getcwd(), "static")

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# Whisper model
whisper_model = whisper.load_model("base")

# API Config
OPENROUTER_API_KEY = "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"

# Cleanup old files function
def cleanup_old_files():
    now = time.time()
    for folder in [UPLOAD_FOLDER, STATIC_FOLDER]:
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            try:
                if os.path.getmtime(path) < now - 3600:  # 1 hour old
                    os.remove(path)
                    print(f"Cleaned up: {path}")
            except Exception as e:
                print(f"Error cleaning {path}: {e}")

# Setup scheduled cleanup
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', hours=1)
scheduler.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process_audio", methods=["POST"])
def process_audio():
    # Generate unique filenames for this request
    timestamp = int(time.time())
    webm_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.webm")
    wav_path = os.path.join(UPLOAD_FOLDER, f"input_{timestamp}.wav")
    output_path = os.path.join(STATIC_FOLDER, f"output_{timestamp}.mp3")

    try:
        # Clean any existing files for this request
        for path in [webm_path, wav_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400

        audio_file = request.files['audio']
        audio_file.save(webm_path)
        os.chmod(webm_path, 0o777)

        # Validate file
        if not os.path.exists(webm_path) or os.path.getsize(webm_path) < 2048:
            raise ValueError("Invalid audio file")

        # Convert to WAV
        subprocess.run([
            "ffmpeg", "-y",
            "-i", webm_path,
            "-ar", "16000",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            wav_path
        ], check=True)

        if not os.path.exists(wav_path):
            raise RuntimeError("Conversion failed")

        # Transcribe
        result = whisper_model.transcribe(wav_path)
        text = re.sub(r'[^\w\s.,!?\'-]', '', result["text"]).strip()
        
        if not text:
            raise ValueError("No speech detected")

        # Generate response
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "google/gemma-3-4b-it",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Keep responses under 30 seconds when spoken."
                    },
                    {"role": "user", "content": text}
                ],
                "max_tokens": 150
            },
            timeout=10
        ).json()['choices'][0]['message']['content']

        # Generate audio with duration check
        response_text = response[:500]
        tts = gTTS(text=response_text, lang='en')
        tts.save(output_path)
        os.chmod(output_path, 0o777)

        # Verify duration
        try:
            result = subprocess.run([
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                output_path
            ], capture_output=True, text=True)
            duration = float(result.stdout.strip())
            if duration > 30:
                tts = gTTS(text="Response too long. Please ask a shorter question.", lang='en')
                tts.save(output_path)
                response = "Response too long. Please ask a more specific question."
        except Exception as e:
            print(f"Duration check failed: {e}")

        return jsonify({
            "text": response,
            "audio": f"/audio/{timestamp}"  # Unique audio URL
        })

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<timestamp>")
def serve_audio(timestamp):
    output_path = os.path.join(STATIC_FOLDER, f"output_{timestamp}.mp3")
    if not os.path.exists(output_path):
        return jsonify({"error": "Audio not found"}), 404
    return send_file(output_path, mimetype="audio/mp3")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)