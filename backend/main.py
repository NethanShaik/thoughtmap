from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import requests
import time
import random
from openai import RateLimitError, APIConnectionError, APITimeoutError, APIStatusError

# ----------------------------
# Configuration / Environment
# ----------------------------
# Local development convenience: load env vars from backend/.env if present.
# In production (Azure/AWS), secrets should be injected via platform env vars / secret stores.

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path = ENV_PATH)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY","").strip()
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL","http://localhost:5173")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "ThoughtMap AI")

# OpenAI SDK configured to use OpenRouter as a compatible gateway.
# Default headers are used by OpenRouter for attribution/analytics
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": OPENROUTER_SITE_URL, 
        "X-Title": OPENROUTER_APP_NAME,       
    },
)

app = FastAPI()

# ----------------------------
# CORS (Cross-Origin Requests)
# ----------------------------
# For local dev when frontend runs on Vite (:5173) and backend runs on :8000.
# In production, the recommended approach is to serve frontend + backend from the same origin,
# which typically removes the need for CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Embedding Model Initialization
# ----------------------------
# Load sentence-transformers model once at startup (expensive operation).
# This is used to embed phrases and compute cosine similarity for the graph edges.
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

#Request Schema
class AnalyzeRequest(BaseModel):
    text:str
    edge_threshold: float

#Text Preprocessing Function
def split_into_phrases(text: str):
    raw = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    raw = sorted(raw, key=len, reverse=True)
    phrases = raw[:10] if len(raw) >= 2 else [text.strip()]
    return phrases

#Compute cosine similarity for set of vectors
def cosine_sim_matrix(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
    v = vectors/norms
    return v @ v.T

#Build semantic graph
#Each phrase becomes a node, edges created between phrases pairs whose cosine similarity>=threshold
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

#LLM Retry
class UpstreamRateLimited(Exception):
    pass

def call_llm_with_retry(client, payload, max_retries=5):

    """
    Call the LLM with exponential backoff for common transient failures:
      - RateLimitError / 429
      - timeouts / connection errors
    """

    last_err = None

    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(**payload)

        
        except RateLimitError as e:
            last_err = e
            sleep_s = min(2 ** attempt, 20) + random.uniform(0, 0.5)
            print(f"Rate limited. Retrying in {sleep_s:.2f}s...")
            time.sleep(sleep_s)

        except APIStatusError as e:
            last_err = e
            if getattr(e, "status_code", None) == 429:
                sleep_s = min(2 ** attempt, 20) + random.uniform(0, 0.5)
                print(f"429 rate limit. Retrying in {sleep_s:.2f}s...")
                time.sleep(sleep_s)
            else:
                raise

        
        except (APITimeoutError, APIConnectionError) as e:
            last_err = e
            sleep_s = min(2 ** attempt, 10) + random.uniform(0, 0.5)
            print(f"Network/timeout. Retrying in {sleep_s:.2f}s...")
            time.sleep(sleep_s)

    
    raise UpstreamRateLimited(f"Upstream rate-limited after {max_retries} retries") from last_err


def gemini_cards(text: str):
    #Generate short cards for main ideam author intent, controversy using LLM
    #Use OpenRouter and requests JSON-only outputs
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
    payload = {
        "model": "google/gemma-3-27b-it:free",
        "messages": [
            {
                "role": "user",
                "content": (
                    "You must output ONLY valid JSON. No markdown, no code fences, no extra text.\n\n"
                    + prompt
                ),
            }
        ],
        "temperature": 0.2,
    }

    resp = call_llm_with_retry(client, payload)

    raw = (resp.choices[0].message.content or "").strip()

     # Defensive cleanup if provider returns fenced code blocks.
    if raw.startswith("```"):
        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw[len("```json"):].strip()
        elif raw.startswith("```"):
            raw = raw[len("```"):].strip()

        if raw.endswith("```"):
            raw = raw[:-3].strip()
    # Parse JSON response; if parsing fails, return raw snippet for debugging.
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "mainIdea": "Could not parse model output as JSON.",
            "authorIntent": "Unknown",
            "controversy": "Unknown",
            "raw": raw[:500],  
        }

# ----------------------------
# API Routes
# ----------------------------
@app.get("/api/models")
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


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """
    Main endpoint:
      1) split text into phrases
      2) generate semantic graph (nodes/edges) via embeddings + cosine similarity
      3) generate LLM "cards" (main idea / intent / controversy)

    Returns both graph data and cards in one response for a single UI action.
    """
    text = (req.text or "").strip()
    if not text:
        return{"error":"Empty text"}
    
    phrases = split_into_phrases(text)
    nodes, edges = build_graph(phrases, req.edge_threshold)
    try:
        cards = gemini_cards(text)
    except RateLimitError:
        cards = {
            "mainIdea": "Provider is temporarily rate-limited. Please retry.",
            "authorIntent": "Unknown",
            "controversy": "Unknown",
        }
    except Exception as e:
        print("LLM ERROR TYPE", type(e))
        print("LLM ERROR:", repr(e))
        cards = {
            "mainIdea": "LLM call failed.",
            "authorIntent": "Unknown",
            "controversy": "Unknown",
            "error": str(e)[:200],
        }
    return{
        "cards": cards,
        "nodes": nodes,
        "edges":edges
    }

# ----------------------------
# Static Frontend Hosting (SPA)
# ----------------------------
# When Docker builds the frontend, it copies the Vite dist/ output into backend/static/.
# We serve:
#   - "/" -> index.html
#   - "/assets/*" -> bundled JS/CSS
#   - any other route -> index.html (SPA routing)
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "static")
INDEX_FILE = os.path.join(FRONTEND_DIST, "index.html")

if os.path.exists(INDEX_FILE):
    #Serve Vite build assets under /assets
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/")
    #Serve the React/Vite index page.
    def serve_index():
        return FileResponse(INDEX_FILE)

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """
        SPA fallback route:
        - Let /api/* and /health behave as API endpoints (return 404 here)
        - For all other paths, return index.html so frontend routing works
        """
        if full_path.startswith("api/") or full_path.startswith("health"):
            return {"detail": "Not Found"}
        return FileResponse(INDEX_FILE)

else:

    @app.get("/")
    def root():
        #Fallback when frontend build is not included in image
        return {"status": "ThoughtMap running (no frontend build found)"}

# ----------------------------
# Health Check
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}