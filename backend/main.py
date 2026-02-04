from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import requests


ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path = ENV_PATH)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY","").strip()
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL","http://localhost:5173")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "ThoughtMap AI")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": OPENROUTER_SITE_URL,  # optional
        "X-Title": OPENROUTER_APP_NAME,        # optional
    },
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

class AnalyzeRequest(BaseModel):
    text:str
    edge_threshold: float = 0.35

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
            score = float(sim[i,j])
            if score >= edge_threshold:
                edges.append({
                    "source": phrases[i],
                    "target": phrases[j],
                    "weight": round(score, 3)
                })
    return nodes, edges

def gemini_cards(text: str):
    if not OPENROUTER_API_KEY:
        return {
            "mainIdea": "OpenRouter not enabled. Add OPENROUTER_API_KEY in backend/.env",
            "authorIntent": "Unknown",
            "controversy": "Unknown",
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
""".strip()
    resp = client.chat.completions.create(
    model="google/gemma-3-27b-it:free",
    messages=[
        {
            "role": "user",
            "content": (
                "You must output ONLY valid JSON. No markdown, no code fences, no extra text.\n\n"
                + prompt
            )
        }
    ],
    temperature=0.2,
)

    raw = (resp.choices[0].message.content or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback instead of crashing your API
        return {
            "mainIdea": "Could not parse model output as JSON.",
            "authorIntent": "Unknown",
            "controversy": "Unknown",
            "raw": raw[:500],  # keep it short so you can debug
        }

    

@app.get("/")
def root():
    return {"Status": "ThoughtMap running"}

@app.get("/models")
def models():
    if not OPENROUTER_API_KEY:
        return {"error": "No OPENROUTER_API_KEY set"}
    r = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json().get("data", [])
    names = [m.get("id") for m in data if m.get("id")]
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