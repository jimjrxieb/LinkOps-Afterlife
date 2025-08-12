import os, chromadb
from dataclasses import dataclass
from typing import List, Dict, Tuple
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

_DB_DIR = os.getenv("CHROMA_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "chroma")))
_COLLECTION = os.getenv("CHROMA_COLLECTION", "afterlife_knowledge")
_EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

_client = None; _collection = None; _embed = None

@dataclass
class Doc:
    id: str; text: str; source: str; title: str = ""; tags: Tuple[str, ...] = ()

def _client_once():
    global _client
    if _client is None:
        os.makedirs(_DB_DIR, exist_ok=True)
        _client = chromadb.PersistentClient(path=_DB_DIR, settings=Settings(anonymized_telemetry=False))
    return _client

def _collection_once():
    global _collection
    if _collection is None:
        _collection = _client_once().get_or_create_collection(_COLLECTION, metadata={"hnsw:space":"cosine"})
    return _collection

def _embedder_once():
    global _embed
    if _embed is None: _embed = SentenceTransformer(_EMBED_MODEL)
    return _embed

def embed_texts(texts: List[str]) -> List[List[float]]:
    return _embedder_once().encode(texts, normalize_embeddings=True).tolist()

def ingest(docs: List[Doc]) -> int:
    col = _collection_once()
    col.add(ids=[d.id for d in docs],
            documents=[d.text for d in docs],
            embeddings=embed_texts([d.text for d in docs]),
            metadatas=[{"source": d.source, "title": d.title, "tags": list(d.tags)} for d in docs])
    return len(docs)

def query(q: str, k: int = 4) -> List[Dict]:
    res = _collection_once().query(query_embeddings=[embed_texts([q])[0]], n_results=k)
    return [{"id": res["ids"][0][i], "text": res["documents"][0][i], "metadata": res["metadatas"][0][i]}
            for i in range(len(res["ids"][0]))]

def format_prompt(question: str, contexts: List[Dict]) -> str:
    ctx = "\n\n".join([f"[{i+1}] {c['metadata'].get('title','')} ({c['metadata'].get('source','')}):\n{c['text']}"
                       for i,c in enumerate(contexts)])
    return ("You are a friendly, concise companion. Use ONLY the context for facts. Cite with [1],[2].\n\n"
            f"Context:\n{ctx}\n\nQuestion: {question}\n\nAnswer:")