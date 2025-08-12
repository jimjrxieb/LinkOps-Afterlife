import os, tempfile, wave, requests

def active_engine(): return os.getenv("TTS_ENGINE","local").lower()

def _silent_wav(seconds=1, sr=16000):
    fd, path = tempfile.mkstemp(suffix=".wav"); os.close(fd)
    with wave.open(path,"w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"\x00\x00" * sr * seconds)
    return path

def synthesize_to_wav(text: str) -> str:
    if active_engine()=="elevenlabs" and os.getenv("ELEVENLABS_API_KEY"):
        voice_id = os.getenv("ELEVENLABS_VOICE_ID","Rachel")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": os.getenv("ELEVENLABS_API_KEY")}
        payload = {"text": text, "model_id": os.getenv("ELEVENLABS_MODEL","eleven_multilingual_v2")}
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        fd, path = tempfile.mkstemp(suffix=".wav"); os.close(fd)
        with open(path,"wb") as f: f.write(r.content)
        return path
    # local stub for Sprint 2 (Piper later)
    return _silent_wav()