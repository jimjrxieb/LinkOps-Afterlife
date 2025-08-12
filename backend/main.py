# /backend/main.py
import os, shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List
from engines.llm_engine import generate_stream
from engines.rag_engine import Doc, ingest as rag_ingest, query as rag_query, format_prompt
from engines.speech_engine import synthesize_to_wav, active_engine as tts_engine
from engines.avatar_engine import lipsync_stub, active_engine as avatar_engine

app = FastAPI(title="AfterLife API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ALLOW_ORIGINS","*")],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)

MEDIA_TMP = os.path.abspath(os.path.join(os.path.dirname(__file__), "media", "tmp"))
os.makedirs(MEDIA_TMP, exist_ok=True)

@app.get("/healthz")
def healthz(): return {"ok": True}

class IngestItem(BaseModel):
    id: str; text: str; source: str; title: str = ""; tags: List[str] = []

@app.post("/ingest")
def ingest(items: List[IngestItem]): 
    n = rag_ingest([Doc(id=i.id, text=i.text, source=i.source, title=i.title, tags=tuple(i.tags)) for i in items])
    return {"ingested": n}

class ChatRequest(BaseModel):
    question: str; k: int = 4

@app.post("/chat")
def chat(req: ChatRequest):
    ctx = rag_query(req.question, k=req.k)
    prompt = format_prompt(req.question, ctx)
    def stream():
        for chunk in generate_stream(prompt): yield chunk
    return StreamingResponse(stream(), media_type="text/plain")

class SpeechRequest(BaseModel): text: str

@app.post("/speech")
def speech(req: SpeechRequest):
    wav = synthesize_to_wav(req.text)
    dst = os.path.join(MEDIA_TMP, os.path.basename(wav)); shutil.copyfile(wav, dst)
    return {"audio_url": f"/media/tmp/{os.path.basename(dst)}", "engine": tts_engine()}

@app.post("/avatar/sync")
def avatar_sync(req: SpeechRequest):
    wav = synthesize_to_wav(req.text)
    dst = os.path.join(MEDIA_TMP, os.path.basename(wav)); shutil.copyfile(wav, dst)
    return lipsync_stub(dst)

@app.get("/media/tmp/{fname}")
def media_tmp(fname: str):
    path = os.path.join(MEDIA_TMP, fname)
    return FileResponse(path)

@app.get("/engines")
def engines():
    return {"tts": tts_engine(), "avatar": avatar_engine()}