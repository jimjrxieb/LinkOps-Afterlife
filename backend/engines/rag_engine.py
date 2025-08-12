# /backend/engines/rag_engine.py
import os
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Sprint 1: Simple in-memory storage
_DOCS = []

@dataclass
class Doc:
    id: str
    text: str
    source: str
    title: str = ""
    tags: Tuple[str, ...] = ()

def ingest(docs: List[Doc]) -> int:
    global _DOCS
    _DOCS.extend(docs)
    return len(docs)

def query(q: str, k: int = 4) -> List[Dict]:
    # Simple keyword matching for Sprint 1
    q_lower = q.lower()
    results = []
    
    for doc in _DOCS:
        if any(word in doc.text.lower() for word in q_lower.split()):
            results.append({
                "id": doc.id,
                "text": doc.text[:500],  # Truncate for demo
                "metadata": {"source": doc.source, "title": doc.title, "tags": list(doc.tags)},
            })
    
    return results[:k]

def format_prompt(question: str, contexts: List[Dict]) -> str:
    if not contexts:
        return f"I don't have specific information about: {question}. This is a demo response."
    
    ctx = "\n\n".join([f"[{i+1}] {c['metadata'].get('title','')} ({c['metadata'].get('source','')}):\n{c['text']}" for i,c in enumerate(contexts)])
    return (
        "You are precise and factual. Use ONLY the context. Cite with [1],[2] etc.\n\n"
        f"Context:\n{ctx}\n\nQuestion: {question}\n\nAnswer:"
    )