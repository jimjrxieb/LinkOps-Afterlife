"""
Pydantic models for the persona system.
Defines the schema for avatar personality configurations.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class PersonaStyle(BaseModel):
    """Defines the communication style and tone of the persona."""
    tone: str = Field(..., description="General tone of responses")
    register: str = Field(..., description="Formality level (casual, neutral, formal)")
    quirks: List[str] = Field(default_factory=list, description="Short stylistic quirks to sprinkle in")


class PersonaBoundaries(BaseModel):
    """Defines safe topics and refusal strategies."""
    safe_topics: List[str] = Field(default_factory=list, description="Topics the persona is comfortable discussing")
    avoid_topics: List[str] = Field(default_factory=list, description="Topics to avoid")
    refusals: List[str] = Field(default_factory=list, description="Stock refusal lines for boundaries")


class PersonaMemory(BaseModel):
    """Core biographical and professional information."""
    bio: str = Field(..., description="Brief personal/professional biography")
    elevator_pitch: str = Field(..., description="Concise professional summary")
    highlights: List[str] = Field(default_factory=list, description="Key accomplishments")
    projects: Dict[str, str] = Field(default_factory=dict, description="Project name to description mapping")
    certs: List[str] = Field(default_factory=list, description="Certifications and qualifications")


class PersonaQA(BaseModel):
    """Pinned Q&A pairs for consistent responses to common questions."""
    pinned: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="List of Q&A pairs: [{'q': 'question', 'a': 'answer'}]"
    )


class PersonaConfig(BaseModel):
    """Complete persona configuration for an AI avatar."""
    id: str = Field(..., description="Unique persona identifier")
    display_name: str = Field(..., description="Human-readable name for the persona")
    style: PersonaStyle = Field(..., description="Communication style configuration")
    boundaries: PersonaBoundaries = Field(..., description="Content boundaries and safety")
    memory: PersonaMemory = Field(..., description="Biographical and professional information")
    qa: PersonaQA = Field(..., description="Pinned Q&A responses")
    tts_voice: Optional[str] = Field(None, description="TTS voice identifier for speech synthesis")
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "james",
                "display_name": "James (LinkOps Creator)",
                "style": {
                    "tone": "Confident, friendly, technical mentor",
                    "register": "neutral",
                    "quirks": ["Uses clear step-by-step lists", "Brief humor when appropriate"]
                },
                "boundaries": {
                    "safe_topics": ["Kubernetes", "DevSecOps", "LinkOps"],
                    "avoid_topics": ["politics", "medical advice"],
                    "refusals": ["Let's keep this focused on my work and technical topics."]
                },
                "memory": {
                    "bio": "I'm James — builder of LinkOps and AfterLife platforms.",
                    "elevator_pitch": "I build secure, self-hosted AI systems for DevOps automation.",
                    "highlights": ["Designed LinkOps AI platform", "CKA certified"],
                    "projects": {"LinkOps": "AI DevOps automation platform"},
                    "certs": ["CKA", "Security+"]
                },
                "qa": {
                    "pinned": [
                        {"q": "What is LinkOps?", "a": "LinkOps is my AI-powered DevOps automation platform."}
                    ]
                },
                "tts_voice": "en_US-male-1"
            }
        }