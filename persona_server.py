#!/usr/bin/env python3
"""
Simple FastAPI server to test persona system locally without full dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Add backend to path
sys.path.append('/home/jimjrxieb/shadow-link-industries/LinkOps-Afterlife/backend')

from persona_loader import load_persona, list_available_personas
from conversation import generate_persona_response

app = FastAPI(title="AfterLife Persona Test Server", version="1.0.0")

# Add Prometheus metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
    print("🔥 Prometheus metrics enabled at /metrics")
except ImportError:
    print("⚠️  Prometheus instrumentator not available")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    persona_id: str = "james"
    context: str = ""

@app.get("/")
async def root():
    return {"message": "AfterLife Persona Test Server", "status": "online"}

@app.get("/healthz")
async def health():
    return {"status": "ok", "service": "persona-test"}

@app.get("/personas")
async def list_personas():
    """List available personas"""
    try:
        personas_dir = "/home/jimjrxieb/shadow-link-industries/LinkOps-Afterlife/data/personas"
        personas = list_available_personas(personas_dir)
        return JSONResponse(
            status_code=200,
            content={"personas": personas, "count": len(personas)}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personas/{persona_id}")
async def get_persona(persona_id: str):
    """Get specific persona details"""
    try:
        personas_dir = "/home/jimjrxieb/shadow-link-industries/LinkOps-Afterlife/data/personas"
        persona = load_persona(persona_id, personas_dir)
        return JSONResponse(
            status_code=200,
            content={
                "persona": {
                    "id": persona.id,
                    "display_name": persona.display_name,
                    "style": {
                        "tone": persona.style.tone,
                        "register": persona.style.register,
                        "quirks": persona.style.quirks
                    },
                    "boundaries": {
                        "safe_topics": persona.boundaries.safe_topics,
                        "avoid_topics": getattr(persona.boundaries, 'avoid_topics', [])
                    },
                    "pinned_qa_count": len(persona.qa.pinned_qa)
                }
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_persona(request: ChatRequest):
    """Chat with a persona"""
    try:
        # Note: generate_persona_response uses default persona directory internally
        response = generate_persona_response(
            request.persona_id, 
            request.message, 
            request.context
        )
        return JSONResponse(status_code=200, content={"response": response})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Persona '{request.persona_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AfterLife Persona Test Server...")
    print("📊 Persona system ready for testing!")
    print("🔗 Access URLs:")
    print("   • Health: http://localhost:8001/healthz")
    print("   • Personas: http://localhost:8001/personas")
    print("   • API Docs: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001)