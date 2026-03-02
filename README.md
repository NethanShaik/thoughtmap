<h1> Thought Map AI </h1>

Visualize how an AI model semantically understands text using embeddings and LLM reasoning!

ThoughtMap AI transforms raw text into:

🔗 A semantic similarity graph

🧾 AI-generated Main Idea

🎯 Detected Author Intent

⚠️ Potential Controversy detection

Deployed on Azure Container Apps with Dockerized full-stack architecture.

🚀 Live Demo

🌐 Production URL:
https://thoughtmap-app.politeplant-9a9d00ed.canadacentral.azurecontainerapps.io)

🏗️ Architecture
```
User Input (React)
        ↓
FastAPI Backend
        ↓
SentenceTransformer Embeddings
        ↓
Cosine Similarity Graph
        ↓
OpenRouter LLM (Gemma)
        ↓
Structured JSON Response
```
⚙️ Tech Stack
<u>Frontend</u>

*React (Vite)
*Tailwind CSS
*ReactFlow (Graph Visualization)

<u>Backend</u>
*FastAPI
*SentenceTransformers (all-MiniLM-L6-v2)
*NumPy
*OpenRouter (LLM API)
*Pydantic

<u>DevOps/Cloud</u>

*Docker (multi-stage build)
*Docker Buildx (multi-arch support)
*Azure Container Registry (ACR)
*Azure Container Apps
*Azure CLI

🧠 How It Works
1) Phrase Extraction
   Text is split into meaningful sentence fragments.

 2)Embedding Generation
   Each phrase is converted into a dense vector using
   
   ```Python
   SentenceTransformer("all-MiniLM-L6-v2")
   ```

3) Cosine Similarity
   Cosine similarity is computed across phrase vectors. Edges are created when similarity exceeds a user-controlled threshold.

4) Graph Construction
   If similarity >= threshold, an edge is created between phrase nodes.

5) LLM Reasoning
   The full text is sent to an LLM (Gemma via OpenRouter) to generate:
   * Main idea
   * Author Inent
   * Controversy detection

🐳 Docker Setup (Local)
Build

```bash
docker build -t thoughtmap .
```
Run

```bash
docker run -p 8000:8000 thoughtmap
```

Open: http://localhost:8000

☁️ Azure Deployment
1) Build multi-arch image
   ```bash
docker buildx build \
  --platform linux/amd64 \
  -t <ACR_LOGIN_SERVER>/thoughtmap:latest \
  --push .
```
