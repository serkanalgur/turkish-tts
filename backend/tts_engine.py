# backend/tts_engine.py
from piper import PiperVoice
import wave
import io
import logging

logger = logging.getLogger(__name__)


class WaveFileBuffer:
    """File-like object implementing wave interface for in-memory buffering."""

    def __init__(self):
        self.buffer = io.BytesIO()
        self.wave_writer = wave.open(self.buffer, "wb")
        self.closed = False

    def setnchannels(self, nchannels):
        self.wave_writer.setnchannels(nchannels)

    def setsampwidth(self, sampwidth):
        self.wave_writer.setsampwidth(sampwidth)

    def setframerate(self, framerate):
        self.wave_writer.setframerate(framerate)

    def writeframes(self, frames):
        self.wave_writer.writeframes(frames)

    def close(self):
        if not self.closed:
            self.wave_writer.close()
            self.closed = True

    def getvalue(self):
        self.close()
        return self.buffer.getvalue()


class TTSEngine:
    def __init__(self, model_path, config_path, use_cuda=False):
        self.model_path = model_path
        self.config_path = config_path
        self.use_cuda = use_cuda
        self.voice = None
        self.load_model()

    def load_model(self):
        try:
            logger.info(f"Loading TTS model: {self.model_path}")
            self.voice = PiperVoice.load(
                model_path=self.model_path,
                config_path=self.config_path,
                use_cuda=self.use_cuda,
            )
            logger.info("TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise

    def synthesize(self, text: str) -> bytes:
        """Synthesize speech and return raw WAV data."""
        if not self.voice:
            raise RuntimeError("TTS model not loaded.")

        wave_buffer = WaveFileBuffer()
        self.voice.synthesize(text=text, wav_file=wave_buffer)
        return wave_buffer.getvalue()
