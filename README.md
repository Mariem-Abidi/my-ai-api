# my-ai-api 🤖

A conversational AI API with RAG (Retrieval-Augmented Generation) and an autonomous web research agent. Built with FastAPI, ChromaDB, and OpenRouter. Deployed on Hugging Face Spaces via Docker.

🚀 **Live demo:** [https://maryyvmm-my-ai-ap.hf.space/docs](https://maryyvmm-my-ai-ap.hf.space/docs)

---

## What it does

- **`/chat`** — Conversational AI with memory (keeps message history per session)
- **`/rag-chat`** — Answers questions using your own documents as context (RAG pipeline)
- **`/agent-chat`** — Autonomous agent that searches the web, synthesizes findings, and saves reports back into the knowledge base automatically

The agent creates a self-improving knowledge loop: it researches topics on the web and feeds the results back into the RAG pipeline, so future questions get richer answers.

---

## Architecture

```
User Request
     │
     ▼
 FastAPI (api.py)
     │
     ├── /chat ──────────────► LLMClient (OpenRouter)
     │                              │
     ├── /rag-chat ──► RAG Pipeline─┤
     │                 (ChromaDB +  │
     │                  HuggingFace)│
     │                              │
     └── /agent-chat ► Agent Loop ──┘
                        │
                        ├── web_search (DuckDuckGo)
                        └── file_write ──► documents/
                                               │
                                               ▼
                                        RAG Pipeline
                                        (auto-ingested)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI |
| LLM | OpenRouter (`openrouter/auto`) |
| Embeddings | HuggingFace `all-MiniLM-L6-v2` |
| Vector Store | ChromaDB |
| Agent Tools | DuckDuckGo Search, File I/O |
| Deployment | Docker + Hugging Face Spaces |

---

## Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Overfitters-lives-matters/my-ai-api.git
cd my-ai-api
```

### 2. Set up environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

### 4. Run locally
```bash
python main.py
# API available at http://localhost:8000/docs
```

---

## API Usage

### Plain chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG in AI?"}'
```

### RAG chat (uses your documents)
```bash
curl -X POST http://localhost:8000/rag-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does our documentation say about X?"}'
```

### Agent chat (researches + saves to knowledge base)
```bash
curl -X POST http://localhost:8000/agent-chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Research the latest trends in vector databases"}'
```

**Agent response includes:**
```json
{
  "response": "Summary of findings...",
  "steps": [
    { "step": 1, "type": "tool_call", "tool": "web_search", "params": {...} },
    { "step": 2, "type": "tool_result", "tool": "web_search", "result": "..." },
    { "step": 3, "type": "tool_call", "tool": "file_write", "params": {...} },
    { "step": 4, "type": "final", "content": "..." }
  ]
}
```

### Conversation history
```bash
GET  /history   # retrieve history
DELETE /history  # clear history
```

---

## Project Structure

```
my-ai-api/
├── src/
│   ├── api.py            # FastAPI routes
│   ├── agent.py          # ReAct agent loop
│   ├── tools.py          # web_search + file_write tools
│   ├── rag.py            # RAG pipeline (ChromaDB)
│   ├── llm_client.py     # OpenRouter LLM wrapper
│   └── conversation.py   # Message history
├── documents/            # Knowledge base (.txt files)
├── Dockerfile
├── main.py
└── requirements.txt
```

---

## Environment Variables

```bash
# .env.example
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your free API key at [openrouter.ai](https://openrouter.ai)

---

## Docker

```bash
docker build -t my-ai-api .
docker run -p 7860:7860 --env-file .env my-ai-api
```

---

## Design Decisions

- **OpenRouter over direct OpenAI** — model-agnostic, easy to switch LLMs without code changes
- **ChromaDB for vector store** — lightweight, no external service needed, persists to disk
- **HuggingFace embeddings** — free, runs locally, no API key needed for embeddings
- **ReAct agent pattern** — LLM decides tool use based on reasoning, not hardcoded rules
- **Agent writes to `documents/`** — closes the loop so researched knowledge enriches future RAG answers

---

## Author

Built mariem abidi