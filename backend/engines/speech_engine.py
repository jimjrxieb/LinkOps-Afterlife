# /backend/engines/speech_engine.py
import os, tempfile, wave

def active_engine() -> str:
    return os.getenv("TTS_ENGINE", "local").lower()

def synthesize_to_wav(text: str) -> str:
    # Sprint 1: local stub (1s silent). Sprint 2: Piper/ElevenLabs branches.
    fd, path = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\x00\x00" * 16000)
    return path