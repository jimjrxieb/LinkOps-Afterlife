import os, requests

def active_engine(): return os.getenv("AVATAR_ENGINE","local").lower()

def lipsync_stub(wav_path: str) -> dict:
    if active_engine()=="did" and os.getenv("DID_API_KEY"):
        # Minimal D-ID "talks" API call using a stock image or user-provided URL
        image_url = os.getenv("DID_IMAGE_URL","https://cdn.didstatic.com/mona_lisa.png")
        with open(wav_path,"rb") as f:
            audio = f.read()
        # Create talk
        r = requests.post(
            "https://api.d-id.com/talks",
            headers={"Authorization": f"Basic {os.getenv('DID_API_KEY')}"},
            json={"source_url": image_url, "driver_url": "bank://lively"},
        )
        r.raise_for_status()
        talk_id = r.json().get("id")
        # Upload audio
        requests.post(
            f"https://api.d-id.com/talks/{talk_id}/audio",
            headers={"Authorization": f"Basic {os.getenv('DID_API_KEY')}"},
            files={"audio": ("speech.wav", audio, "audio/wav")}
        ).raise_for_status()
        # Poll result (simplified)
        for _ in range(20):
            s = requests.get(f"https://api.d-id.com/talks/{talk_id}",
                             headers={"Authorization": f"Basic {os.getenv('DID_API_KEY')}"}, timeout=10)
            s.raise_for_status()
            data = s.json()
            if data.get("result_url"):
                return {"audio_url": None, "video_url": data["result_url"], "engine": "did"}
        return {"audio_url": None, "video_url": None, "engine": "did", "note":"timeout"}
    # local fallback
    import os as _os
    return {"audio_url": f"/media/tmp/{_os.path.basename(wav_path)}", "video_url": None, "engine": "local"}