# /backend/engines/avatar_engine.py
import os
def active_engine() -> str:
    return os.getenv("AVATAR_ENGINE", "local").lower()

def lipsync_stub(wav_path: str) -> dict:
    return {"audio_url": f"/media/tmp/{os.path.basename(wav_path)}", "video_url": None, "engine": active_engine()}