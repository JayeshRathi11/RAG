import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

try:
    from server import app
except (ImportError, ValueError):
    from .server import app


def main():
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"[INFO] Starting RAG Queue API server on http://localhost:{port}")
    uvicorn.run(app, port=port, host=host)


if __name__ == "__main__":
    main()