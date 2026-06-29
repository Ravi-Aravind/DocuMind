# DocuMind

> **An AI-powered Retrieval-Augmented Generation (RAG) platform for document intelligence.**

DocuMind is a full-stack Retrieval-Augmented Generation (RAG) application that enables users to upload documents, automatically ingest and index them into a vector database, and ask natural language questions grounded entirely on the uploaded content.

The project is being developed with a strong emphasis on **backend architecture, modularity, scalability, and production-ready engineering practices** rather than simply building an AI demo.

---

# Current Status

## Backend

* ✅ FastAPI application
* ✅ PostgreSQL integration
* ✅ SQLAlchemy 2.x ORM
* ✅ Alembic migrations
* ✅ JWT Authentication
* ✅ Google OAuth
* ✅ Document upload
* ✅ PDF / DOCX / TXT / Markdown parsing
* ✅ Chunking pipeline
* ✅ Embedding generation
* ✅ Qdrant vector indexing
* ✅ SearchService abstraction
* ✅ HybridRetriever
* ✅ BGE Reranker
* ✅ PromptBuilder abstraction
* ✅ OpenRouter service abstraction
* 🚧 Full end-to-end QA validation
* 🚧 Worker queue
* 🚧 Hybrid Search
* 🚧 Multi-provider LLM support

---

# Architecture

```
                User
                 │
                 ▼
         FastAPI REST API
                 │
      ┌──────────┴──────────┐
      │                     │
 Authentication      Document Upload
      │                     │
      ▼                     ▼
 PostgreSQL          Local File Storage
                            │
                            ▼
                      Document Parser
                            │
                            ▼
                         Chunker
                            │
                            ▼
                      Embedding Model
                            │
                            ▼
                        Qdrant
                            │
                            ▼
                    SearchService
                     /          \
        HybridRetriever     BGEReranker
                     \          /
                      Retrieved Chunks
                            │
                            ▼
                     PromptBuilder
                            │
                            ▼
                    OpenRouterService
                            │
                            ▼
                      Generated Answer
```

---

# Project Structure

```
backend/
│
├── app/
│   ├── api/
│   ├── config.py
│   ├── db/
│   │     ├── models/
│   │     ├── base.py
│   │     └── session.py
│   │
│   ├── rag/
│   │     ├── parsers/
│   │     ├── retrieval/
│   │     ├── pipeline/
│   │     ├── embeddings.py
│   │     └── qdrant_client.py
│   │
│   ├── prompts/
│   ├── services/
│   ├── schemas/
│   └── llm/
│
├── alembic/
│
└── tests/
```

---

# Technology Stack

## Backend

* Python 3.12+
* FastAPI
* SQLAlchemy 2.x
* Alembic
* Pydantic v2
* AsyncPG

## AI / RAG

* Sentence Transformers
* BAAI/bge-large-en-v1.5
* BAAI/bge-reranker-large
* Qdrant
* OpenRouter

## Database

* PostgreSQL

## Frontend

* Next.js
* React
* TypeScript

---

# Environment Variables

Create a `.env` file in the **project root**.

```
DocuMind/
│
├── .env
├── backend/
└── frontend/
```

---

## Application

```env
APP_NAME=DocuMind Backend
ENVIRONMENT=development
```

---

## JWT

Generate two secure random strings.

Example:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

```
SECRET_KEY=your_secret_key
REFRESH_SECRET_KEY=your_refresh_secret_key
```

---

## PostgreSQL

```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=documind
```

### Notes

Create the database first.

```sql
CREATE DATABASE documind;
```

If your password contains special characters (`@`, `#`, `%`, etc.), the application automatically handles URL construction.

---

## Google OAuth

Create OAuth credentials from Google Cloud Console.

```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

---

## Qdrant

Install and run Qdrant locally.

```
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=documents_bge_large
```

No API key is required for local Docker deployments.

---

## Embedding Model

```
EMBEDDING_MODEL_NAME=BAAI/bge-large-en-v1.5
```

---

## Reranker

```
RERANKER_MODEL_NAME=BAAI/bge-reranker-large
```

---

## Retrieval

```
VECTOR_TOP_K=10
BM25_TOP_K=10
RERANK_TOP_K=5
RRF_K=60
SEARCH_TIMEOUT=30
```

---

## OpenRouter

Create an account at OpenRouter.

Generate an API Key.

```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx
OPENROUTER_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
OPENROUTER_MODEL=anthropic/claude-3.5-haiku
```

---

## LLM

```
LLM_TIMEOUT=60
LLM_TEMPERATURE=0.1
```

---

# Installation

Clone the repository.

```bash
git clone <repo-url>
cd DocuMind
```

---

## Backend

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## PostgreSQL

Create the database.

```sql
CREATE DATABASE documind;
```

---

## Run Alembic

Generate tables.

```bash
alembic upgrade head
```

Verify.

```sql
SELECT tablename
FROM pg_tables
WHERE schemaname='public';
```

Expected:

```
users
collections
documents
qa_sessions
qa_messages
session_documents
alembic_version
```

---

## Qdrant

Run with Docker.

```bash
docker run -p 6333:6333 qdrant/qdrant
```

Verify.

```
http://localhost:6333/dashboard
```

---

# Running the Backend

Start FastAPI.

```bash
uvicorn backend.app.main:app --reload
```

Swagger UI:

```
http://localhost:8000/docs
```

OpenAPI:

```
http://localhost:8000/openapi.json
```

---

# Expected Workflow

## Upload

```
POST /documents/upload
```

↓

File stored locally

↓

Parser

↓

Chunker

↓

Embedding

↓

Qdrant Index

↓

Status = READY

---

## Question Answering

```
POST /qa/ask
```

↓

SearchService

↓

HybridRetriever

↓

BGEReranker

↓

PromptBuilder

↓

OpenRouter

↓

Grounded Answer

---

# Testing

Run all tests.

```bash
pytest
```

Run a specific module.

```bash
pytest backend/tests/test_search_service.py
```

---

# Current Backend Components

| Component          | Status                 |
| ------------------ | ---------------------- |
| Authentication     | ✅                      |
| PostgreSQL         | ✅                      |
| Alembic            | ✅                      |
| Upload             | ✅                      |
| Parsing            | ✅                      |
| Chunking           | ✅                      |
| Embeddings         | ✅                      |
| Qdrant             | ✅                      |
| SearchService      | ✅                      |
| HybridRetriever    | ✅                      |
| BGE Reranker       | ✅                      |
| PromptBuilder      | ✅                      |
| OpenRouter Service | ✅                      |
| QA Pipeline        | 🚧 Integration Testing |
| Background Worker  | 🚧                     |
| Hybrid Search      | 🚧                     |
| Multi-Provider LLM | 🚧                     |

---

# Roadmap

## Phase 1 — Backend Foundation ✅

* FastAPI
* PostgreSQL
* Alembic
* Authentication
* Upload pipeline
* SearchService architecture

## Phase 2 — RAG Integration 🚧

* End-to-end ingestion
* End-to-end QA
* Citation verification
* Integration testing

## Phase 3 — Production Features

* Celery/RQ workers
* Redis
* S3/Blob Storage
* Hybrid Search
* Metadata Filtering
* Observability
* Metrics
* Monitoring

---

# License

This project is intended for educational, research, and portfolio purposes.