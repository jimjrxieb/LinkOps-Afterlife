# /backend/preprocess.py
import os, glob, re, yaml
from engines.rag_engine import ingest, Doc

ROOT = "/app"
DATA = "/app/data"

def md_chunks(path: str, tag="project"):
    with open(path, "r", encoding="utf-8") as f: txt = f.read()
    parts = re.split(r"\n#{1,6}\s+", txt)
    docs = []
    for i, p in enumerate(parts):
        p = p.strip()
        if not p: continue
        docs.append(Doc(id=f"{tag}:{os.path.basename(path)}:{i}", text=p[:4000], source=path, title=os.path.basename(path), tags=(tag,)))
    return docs

def yaml_doc(path: str, tag="persona"):
    with open(path, "r", encoding="utf-8") as f: y = yaml.safe_load(f)
    flat = yaml.safe_dump(y)
    return [Doc(id=f"{tag}:{os.path.basename(path)}", text=flat[:4000], source=path, title=os.path.basename(path), tags=(tag,))]

def seed():
    docs = []
    # persona (you)
    for y in glob.glob(os.path.join(DATA, "personas", "*.yaml")):
        docs += yaml_doc(y, "persona")
    # top-level README (check /app/project_root if volume mounted)
    for readme_path in ["/app/project_root/README.md", os.path.join(ROOT, "README.md"), "/app/README.md"]:
        if os.path.exists(readme_path): 
            docs += md_chunks(readme_path, "project")
            break
    return ingest(docs)

if __name__ == "__main__":
    print({"ingested": seed()})