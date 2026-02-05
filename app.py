import base64
import io
import numpy as np
import librosa
from flask import Flask, request, jsonify
from pydub import AudioSegment

app = Flask(__name__)

API_KEY = "sk_test_123456"

SUPPORTED_LANGS = ["Tamil", "English", "Hindi", "Malayalam", "Telugu"]


def analyze_audio(audio_bytes):
    audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    y, sr = librosa.load(wav_io, sr=None)

    pitch = librosa.yin(y, fmin=50, fmax=400)
    pitch_var = np.var(pitch[np.isfinite(pitch)])

    # Simple beginner rule
    if pitch_var < 5:
        return "AI_GENERATED", 0.85, "Low pitch variation suggests synthetic voice"
    else:
        return "HUMAN", 0.80, "Natural pitch variation detected"


@app.route("/api/voice-detection", methods=["POST"])
def detect():

    if request.headers.get("x-api-key") != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API key"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Bad request"}), 400

    language = data.get("language")
    audio_b64 = data.get("audioBase64")

    if language not in SUPPORTED_LANGS or not audio_b64:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    try:
        audio_bytes = base64.b64decode(audio_b64)
        classification, confidence, explanation = analyze_audio(audio_bytes)

        return jsonify({
            "status": "success",
            "language": language,
            "classification": classification,
            "confidenceScore": confidence,
            "explanation": explanation
        })

    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": "Audio processing failed"}), 500


if __name__ == "__main__":
    app.run(debug=True)
