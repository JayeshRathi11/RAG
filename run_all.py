import os
import sys
import time
import subprocess
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


def check_services():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    try:
        r = Redis(host=redis_host, port=redis_port)
        r.ping()
        print(f"[OK] Redis connection verified at {redis_host}:{redis_port}")
    except Exception as e:
        print(f"[ERROR] Redis is not reachable at {redis_host}:{redis_port}: {e}")
        print("Please ensure Redis is running (e.g., via Docker).")
        sys.exit(1)


def main():
    print("==================================================")
    print("Starting Complete RAG Queue System")
    print("==================================================")

    check_services()

    worker_script = str(BASE_DIR / "run_worker.py")
    server_script = str(BASE_DIR / "main.py")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    print("\n[1/2] Starting RQ Background Worker...")
    worker_proc = subprocess.Popen([sys.executable, worker_script], env=env)
    time.sleep(1)

    print("\n[2/2] Starting FastAPI Web Server...")
    try:
        server_proc = subprocess.Popen([sys.executable, server_script], env=env)
        
        print("\n==================================================")
        print("All systems running!")
        print(" - FastAPI Server:  http://localhost:8000")
        print(" - API Docs:        http://localhost:8000/docs")
        print(" - RQ Worker:       Active & Listening on Redis")
        print("==================================================\n")
        
        while True:
            time.sleep(1)
            if worker_proc.poll() is not None:
                print("[WARNING] Worker process exited.")
                break
            if server_proc.poll() is not None:
                print("[WARNING] Server process exited.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down services...")
    finally:
        worker_proc.terminate()
        try:
            server_proc.terminate()
        except Exception:
            pass
        print("[OK] Shutdown complete.")


if __name__ == "__main__":
    main()
