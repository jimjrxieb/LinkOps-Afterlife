import os, io, time, shutil, zipfile, json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import uuid

router = APIRouter()
TMP_ROOT = os.getenv("TMP_ROOT", "/app/tmp")
JOB_TTL_SEC = int(os.getenv("JOB_TTL_SEC", "1800"))  # 30 min default

def job_path(job_id: str) -> str:
    return os.path.join(TMP_ROOT, job_id)

class BuildRequest(BaseModel):
    name: str = "Avatar"
    memories: List[str] = []
    personality: Dict[str, Any] = {}
    voice_sample: str = ""
    
class BuildResult(BaseModel):
    job_id: str
    files: List[str]
    expires_in: int

@router.post("/wizard/build")
def build_avatar(req: BuildRequest):
    """Build avatar assets in temp workspace"""
    job_id = str(uuid.uuid4())
    workspace = job_path(job_id)
    os.makedirs(workspace, exist_ok=True)
    os.makedirs(os.path.join(workspace, "memory"), exist_ok=True)
    
    files = []
    
    # Create avatar placeholder image
    avatar_path = os.path.join(workspace, "avatar.png")
    # Create a simple 1x1 PNG placeholder (real implementation would process uploaded photos)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
    with open(avatar_path, 'wb') as f:
        f.write(png_data)
    files.append("avatar.png")
    
    # Create TTS sample (placeholder WAV)
    if req.voice_sample:
        from engines.speech_engine import synthesize_to_wav
        wav_path = synthesize_to_wav(req.voice_sample[:100])  # Short sample
        sample_path = os.path.join(workspace, "sample_speech.wav")
        shutil.copy(wav_path, sample_path)
        os.unlink(wav_path)  # cleanup temp
        files.append("sample_speech.wav")
    
    # Save memories as JSONL
    if req.memories:
        memories_path = os.path.join(workspace, "memory", "memories.jsonl")
        with open(memories_path, 'w') as f:
            for i, memory in enumerate(req.memories):
                f.write(json.dumps({
                    "id": f"memory_{i}",
                    "text": memory,
                    "source": "user_input",
                    "timestamp": time.time()
                }) + '\n')
        files.append("memory/memories.jsonl")
    
    # Save persona config
    persona_data = {
        "id": job_id,
        "display_name": req.name,
        "style": req.personality.get("style", {}),
        "memory": {"bio": req.personality.get("bio", "")},
        "created": time.time()
    }
    persona_path = os.path.join(workspace, "memory", "persona.yaml")
    import yaml
    with open(persona_path, 'w') as f:
        yaml.dump(persona_data, f, default_flow_style=False)
    files.append("memory/persona.yaml")
    
    # Create config.json
    config = {
        "job_id": job_id,
        "name": req.name,
        "created": time.time(),
        "engines": {
            "llm": "Qwen/Qwen2.5-1.5B-Instruct",
            "tts": "local",
            "avatar": "local"
        }
    }
    config_path = os.path.join(workspace, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    files.append("config.json")
    
    # Create README
    readme_content = f"""# {req.name} Avatar Pack

This package was created with LinkOps Afterlife (demo.linkopsmlm.com).

## Contents:
- avatar.png: Profile image
- sample_speech.wav: Voice sample (if provided)
- memory/memories.jsonl: Your uploaded memories
- memory/persona.yaml: Personality configuration  
- config.json: Build settings

## To run locally:
1. Clone: git clone https://github.com/shadow-link-industries/LinkOps-Afterlife
2. Copy this pack to: data/personas/{job_id}/
3. Run: docker compose up --build -d
4. Import: docker compose exec api python preprocess.py

Your avatar will be available for chat at http://localhost:5173

Created: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
Expires: This pack auto-deletes in ~30 minutes from the demo server.
"""
    readme_path = os.path.join(workspace, "README.txt")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    files.append("README.txt")
    
    return BuildResult(
        job_id=job_id,
        files=files,
        expires_in=JOB_TTL_SEC
    )

@router.get("/wizard/export/{job_id}.zip")
def export_job(job_id: str):
    """Download avatar pack as zip"""
    path = job_path(job_id)
    if not os.path.isdir(path):
        raise HTTPException(404, "Job not found or already purged")
    
    def gen():
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for root, _, files in os.walk(path):
                for f in files:
                    full = os.path.join(root, f)
                    arc = os.path.relpath(full, path)
                    z.write(full, arc)
        buf.seek(0)
        # Stream in chunks to avoid memory issues
        while True:
            chunk = buf.read(1024 * 1024)  # 1MB chunks
            if not chunk: 
                break
            yield chunk
    
    return StreamingResponse(
        gen(), 
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{job_id}.zip"'}
    )

@router.post("/wizard/purge/{job_id}")
def purge_job(job_id: str):
    """Delete avatar pack immediately"""
    path = job_path(job_id)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        return {"purged": job_id, "status": "deleted"}
    return {"status": "not_found"}

@router.get("/wizard/jobs")
def list_jobs():
    """List active jobs (for debugging)"""
    os.makedirs(TMP_ROOT, exist_ok=True)
    jobs = []
    now = time.time()
    for name in os.listdir(TMP_ROOT):
        p = os.path.join(TMP_ROOT, name)
        if os.path.isdir(p):
            age = now - os.path.getmtime(p)
            jobs.append({
                "job_id": name,
                "age_seconds": int(age),
                "expires_in": max(0, JOB_TTL_SEC - int(age))
            })
    return {"jobs": jobs}

def purge_expired():
    """Background cleanup function"""
    now = time.time()
    os.makedirs(TMP_ROOT, exist_ok=True)
    purged = 0
    for name in os.listdir(TMP_ROOT):
        p = os.path.join(TMP_ROOT, name)
        if not os.path.isdir(p): 
            continue
        age = now - os.path.getmtime(p)
        if age > JOB_TTL_SEC:
            shutil.rmtree(p, ignore_errors=True)
            purged += 1
    return purged