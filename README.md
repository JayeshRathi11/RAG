# Asynchronous RAG Queue Pipeline

A high-performance, asynchronous Retrieval-Augmented Generation (RAG) backend. Instead of blocking HTTP request threads with expensive vector searches and LLM completions, this architecture offloads jobs to an asynchronous **Redis Queue (RQ)** worker pool.

---

## Architecture Overview

```
                      +-------------------+
                      |   Client / User   |
                      +---------+---------+
                                |
             1. POST /chat?query=...  (Returns job_id immediately)
                                v
                      +-------------------+
                      |   FastAPI Server  | (Port 8008)
                      +---------+---------+
                                |
                   2. Enqueues job to Redis
                                v
                      +-------------------+
                      |    Redis Queue    | (Port 6379)
                      +---------+---------+
                                |
                   3. Worker pops and executes job
                                v
                      +-------------------+
                      |  RQ Worker Process| (SimpleWorker)
                      +----+---------+----+
                           |         |
     4. Similarity Search  |         | 5. Augmented Prompt Completion
                           v         v
                   +-----------+  +------------------+
                   |  Qdrant   |  | OpenAI / Mock AI |
                   | Vector DB |  |  (gpt-4o-mini)   |
                   +-----------+  +------------------+
```

---

## Prerequisites & Infrastructure

1. **Redis Server** (Port `6379`):
   Running in Docker container `redis-stack` on `127.0.0.1:6379`.
2. **Qdrant Vector Database** (Port `6333`):
   Running in Docker container `qdrant-db` on `127.0.0.1:6333`.
3. **Python 3.14+ Dependencies**:
   Installed (`fastapi`, `uvicorn`, `redis`, `rq`, `langchain`, `langchain-openai`, `langchain-qdrant`, `qdrant-client`, `langchain-community`, `pypdf`, `python-dotenv`).

---

## How to Run

### 1. Run Complete Project (Server + Worker)
Launch both the background worker and the FastAPI server with one command:
```bash
python run_all.py
```

### 2. Run Components Individually (Optional)
- **Start Worker only:**
  ```bash
  python run_worker.py
  ```
- **Start FastAPI Server only:**
  ```bash
  python main.py
  ```

---

## API Endpoints

Interactive Swagger documentation is available at: [http://localhost:8008/docs](http://localhost:8008/docs)

### 1. Health & Server Status
- **URL**: `GET http://localhost:8008/`
- **Response**:
  ```json
  {
    "status": "Server is up and running",
    "mode": "mock_demo",
    "queue_name": "default"
  }
  ```

### 2. Submit Chat Query (Asynchronous)
- **URL**: `POST http://localhost:8008/chat?query=How does the Node.js event loop work?`
- **Response**:
  ```json
  {
    "status": "queued",
    "job_id": "47026c2b-5e8d-4c5a-be56-d7651a58958f",
    "message": "Query successfully dispatched to background Redis queue."
  }
  ```

### 3. Check Job Status & Retrieve Result
- **URL**: `GET http://localhost:8008/job-status?job_id=<job_id>`
- **Response** (When Finished):
  ```json
  {
    "job_id": "47026c2b-5e8d-4c5a-be56-d7651a58958f",
    "status": "finished",
    "result": "Based on Page 12 of 'nodejs.pdf'...",
    "error": null
  }
  ```

---

## Switching to Live OpenAI & Qdrant

By default, the system runs in **Mock/Demo mode** if no OpenAI key is configured.

To enable live OpenAI embeddings and LLM completions:
1. Open `.env`:
   ```env
   OPENAI_API_KEY=sk-...
   ```
2. Run document indexing (indexes `nodejs.pdf` into Qdrant collection `learning_rag`):
   ```bash
   python index_documents.py
   ```
3. Restart the system:
   ```bash
   python run_all.py
   ```
