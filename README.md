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
