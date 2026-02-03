from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import numpy as np

from sentence_transformers import SentenceTransformer
from google import genai


load_dotenv()
print("PWD:", os.getcwd())
print("GEMINI_API_KEY loaded?", bool(os.getenv("GEMINI_API_KEY")))
print("Key starts with:", (os.getenv("GEMINI_API_KEY") or "")[:6])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY","")
client = genai.Client(api_key = GEMINI_API_KEY)

class AnalyzeRequest(BaseModel):
    text:str
    edge_threshold: float = 0.55

def split_into_phrases(text: str):
    raw = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    raw = sorted(raw, key=len, reverse=True)
    phrases = raw[:10] if len(raw) >= 3 else [text.strip()]
    return phrases

def cosine_sim_matrix(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
    v = vectors/norms
    return v @ v.T

def build_graph(phrases, edge_threshold: float):
    emb = embed_model.encode(phrases, convert_to_numpy=True)
    sim = cosine_sim_matrix(emb)
    nodes = [{"id":p, "label": p} for p in phrases]
    edges = []

    for i in range(len(phrases)):
        for j in range(i+1, len(phrases)):
            score = floar(sim[i,j])
            if score >= edge_threshold:
                edges.append({
                    "source": phrases[i],
                    "target": phrases[j],
                    "weight": round(score, 3)
                })
    return nodes, edges

def gemini_cards(text: str):
    if client is None:
        return{
            "mainIdea": "Gemini not enabled. Add GEMINI_API_KEY in backend/.env",
            "authorIntent": "Unknown",
            "controversy": "Unknown"
        }
    
    prompt = f"""
Return ONLY valid JSON with keys:
mainIdea, authorIntent, controversy

Rules:
- mainIdea: 1-2 sentences
- authorIntent: one short label (Inform/Explain/Persuade/Argue/Narrate/etc.)
- controversy: "None detected" OR 1 sentence describing risk

TEXT:
{text}
"""
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    raw = resp.text.strip()
    return json.loads(raw)

@app.get("/")
def root():
    return {"Status": "ThoughtMap running"}

@app.get("/models")
def models():
    if not client:
        return {"error": "No GEMINI_API_KEY set"}
    names = []
    for m in client.models.list():
        names.append(m.name)
    return {"models": names[:50], "count": len(names)}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    text = (req.text or "").strip()
    if not text:
        return{"error":"Empty text"}
    
    phrases = split_into_phrases(text)
    nodes, edges = build_graph(phrases, req.edge_threshold)

    cards = gemini_cards(text)

    return{
        "cards": cards,
        "nodes": nodes,
        "edges":edges
    }