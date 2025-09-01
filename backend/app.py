# backend/app.py
from flask import Flask, request, Response, send_file
import logging
import os

from tts_engine import TTSEngine
from num2words_tr import turkish_number_to_words

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    static_url_path="",
    static_folder="../frontend",
)

# Initialize TTS Engine
# tts_engine = TTSEngine(
#    model_path="/app/models/tr_TR-dfki-medium.onnx",
#    config_path="/app/models/tr_TR-dfki-medium.onnx.json",
# )

model_paths = {
    "dfki": {
        "model": "/app/models/tr_TR-dfki-medium.onnx",
        "config": "/app/models/tr_TR-dfki-medium.onnx.json",
    },
    "fahrettin": {
        "model": "/app/models/tr_TR-fahrettin-medium.onnx",
        "config": "/app/models/tr_TR-fahrettin-medium.onnx.json",
    },
}


@app.route("/")
def index():
    return send_file(app.static_folder + "/index.html")


@app.route("/generate-speech", methods=["POST"])
def generate_speech():
    data = request.get_json()
    text = data.get("text", "").strip()
    language = data.get("language", "tr-TR")
    speaker = data.get("speaker", "dfki")  # or fahrettin

    tts_engine = TTSEngine(
        model_path=model_paths[speaker]["model"],
        config_path=model_paths[speaker]["config"],
    )

    if not text:
        return {"error": "No text provided"}, 400

    # Normalize text based on language
    if language == "tr-TR":
        normalized_text = turkish_number_to_words(text)
        logger.info(f"[TR] Normalized: '{text}' → '{normalized_text}'")
    else:
        normalized_text = text

    try:
        audio_data = tts_engine.synthesize(normalized_text)
        return Response(
            audio_data,
            mimetype="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"},
        )
    except Exception as e:
        logger.error(f"TTS generation failed: {e}", exc_info=True)
        return {"error": f"Speech generation failed: {str(e)}"}, 500


@app.route("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": "tr_TR-dfki-medium",
        "languages": ["tr-TR"],
        "number_handling": "advanced",
        "piper_version": "1.2.0",
        "api_style": "requires_wav_file_parameter",
        "buffer_implementation": "wave_file_interface",
    }


if __name__ == "__main__":
    logger.info("Starting TTS server on 0.0.0.0:5002")
    app.run(host="0.0.0.0", port=5002, debug=True)
