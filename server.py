import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure the root project directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

from fastapi import FastAPI, Query, HTTPException

try:
    from client.rq_client import queue
    from queues.worker import process_query, USE_LIVE_OPENAI
except (ImportError, ValueError):
    from .client.rq_client import queue
    from .queues.worker import process_query, USE_LIVE_OPENAI


app = FastAPI(
    title="RAG Queue API",
    description="Asynchronous RAG pipeline offloading document retrieval and AI completion to background RQ workers.",
    version="1.0.0"
)


@app.get('/')
def root():
    return {
        "status": "Server is up and running",
        "mode": "live_openai" if USE_LIVE_OPENAI else "mock_demo",
        "queue_name": queue.name,
        "endpoints": {
            "chat": "POST /chat?query=...",
            "job_status": "GET /job-status?job_id=...",
            "docs": "/docs"
        }
    }


@app.post('/chat')
def chat(
    query: str = Query(..., description="The chat query of user")
):
    try:
        job = queue.enqueue(process_query, query)
        return {
            "status": "queued",
            "job_id": job.id,
            "message": "Query successfully dispatched to background Redis queue."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")


@app.get('/job-status')
def get_result(
    job_id: str = Query(..., description="Job ID")
):
    job = queue.fetch_job(job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")

    status = job.get_status()
    result = job.result if job.is_finished else None
    error = str(job.exc_info) if job.is_failed else None

    return {
        "job_id": job_id,
        "status": status,
        "result": result,
        "error": error
    }