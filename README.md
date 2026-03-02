# ThoughtMap AI

Visualize how an AI model semantically understands text using embeddings and LLM reasoning!

ThoughtMap AI transforms raw text into:

- 🔗 A semantic similarity graph  
- 🧾 AI-generated **Main Idea**  
- 🎯 Detected **Author Intent**  
- ⚠️ Potential **Controversy detection**

Deployed on **Azure Container Apps** with a Dockerized full-stack architecture.

---

## 🚀 Live Demo

🌐 **Production URL**  
https://thoughtmap-app.politeplant-9a9d00ed.canadacentral.azurecontainerapps.io

---

## 🏗️ Architecture

```
User Input (React)
        ↓
FastAPI Backend
        ↓
SentenceTransformer Embeddings
        ↓
Cosine Similarity Matrix
        ↓
Graph Construction
        ↓
OpenRouter LLM (Gemma)
        ↓
Structured JSON Response
```

---

## ⚙️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- ReactFlow (Graph Visualization)

### Backend
- FastAPI
- SentenceTransformers (`all-MiniLM-L6-v2`)
- NumPy
- OpenRouter (LLM API)
- Pydantic

### DevOps / Cloud
- Docker (multi-stage build)
- Docker Buildx (multi-arch support)
- Azure Container Registry (ACR)
- Azure Container Apps
- Azure CLI

---

## 🧠 How It Works

### 1️⃣ Phrase Extraction
Text is split into meaningful sentence fragments.

### 2️⃣ Embedding Generation
Each phrase is converted into a dense vector using:

```python
SentenceTransformer("all-MiniLM-L6-v2")
```

### 3️⃣ Cosine Similarity
Cosine similarity is computed across phrase vectors.  
Edges are created when similarity exceeds a user-controlled threshold.

### 4️⃣ Graph Construction
Phrases become nodes.  
Similarity relationships become edges.

### 5️⃣ LLM Reasoning
The full text is sent to a Gemma LLM (via OpenRouter) to generate:

- Main Idea  
- Author Intent  
- Controversy detection  

---

## 🐳 Docker Setup (Local)

### Build

```bash
docker build -t thoughtmap .
```

### Run

```bash
docker run -p 8000:8000 thoughtmap
```

Open:

```
http://localhost:8000
```

---

## ☁️ Azure Deployment

### 1️⃣ Build multi-arch image

```bash
docker buildx build \
  --platform linux/amd64 \
  -t <ACR_LOGIN_SERVER>/thoughtmap:latest \
  --push .
```

### 2️⃣ Deploy to Azure Container Apps

```bash
az containerapp create \
  -n thoughtmap-app \
  -g thoughtmap-rg \
  --environment thoughtmap-env \
  --image <ACR_LOGIN_SERVER>/thoughtmap:latest \
  --ingress external \
  --target-port 8000
```
