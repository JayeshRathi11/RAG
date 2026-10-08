import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

from redis import Redis
from rq import SimpleWorker, Queue


def main():
    redis_host = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    print(f"Connecting to Redis at {redis_host}:{redis_port}...")
    redis_conn = Redis(host=redis_host, port=redis_port)

    try:
        redis_conn.ping()
        print("Connected to Redis successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Redis: {e}")
        sys.exit(1)

    listen_queues = [Queue("default", connection=redis_conn)]
    print("[INFO] Starting RQ Worker (SimpleWorker for Windows compatibility)...")
    print("[INFO] Worker is now actively listening for queued jobs on 'default' queue...")
    
    worker = SimpleWorker(listen_queues, connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
