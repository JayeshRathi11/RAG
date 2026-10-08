import os
import sys
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "learning_rag")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

USE_LIVE_OPENAI = bool(OPENAI_API_KEY and not OPENAI_API_KEY.startswith("your_"))

vector_db = None
openai_client = None

if USE_LIVE_OPENAI:
    try:
        from openai import OpenAI
        from langchain_openai import OpenAIEmbeddings
        from langchain_qdrant import QdrantVectorStore

        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-large",
            api_key=OPENAI_API_KEY
        )
        try:
            vector_db = QdrantVectorStore.from_existing_collection(
                url=QDRANT_URL,
                collection_name=QDRANT_COLLECTION,
                embedding=embedding_model,
            )
            print(f"[OK] Connected to live Qdrant collection '{QDRANT_COLLECTION}'")
        except Exception as qdrant_err:
            print(f"[WARN] Qdrant collection '{QDRANT_COLLECTION}' not yet created ({qdrant_err}). Live search will fall back gracefully.")
            vector_db = None
    except Exception as e:
        print(f"[WARN] Error initializing OpenAI client: {e}")
        USE_LIVE_OPENAI = False


def process_query(query: str) -> str:
    """
    RQ worker task: processes a user's RAG chat query.
    Note: Function is defined as synchronous 'def' because RQ executes jobs synchronously.
    """
    print(f"\n[Worker] Processing query: '{query}'")

    if USE_LIVE_OPENAI and openai_client:
        if vector_db:
            print(f"[Worker] Searching Qdrant vector database for: '{query}'")
            search_results = vector_db.similarity_search(query=query)
            context = "\n\n\n".join([
                f"Page Content: {result.page_content}\nPage Number: {result.metadata.get('page_label', 'N/A')}\nFile Location: {result.metadata.get('source', 'nodejs.pdf')}"
                for result in search_results
            ])
        else:
            context = "Document context: Node.js is an open-source, cross-platform JavaScript runtime environment."

        system_prompt = f"""You are a helpful AI Assistant who answers user queries based on the available context retrieved from a PDF file along with page_contents and page number.

You should only answer the user based on the following context and navigate the user to open the right page number to know more.

Context:
{context}
"""
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ]
        )
        answer = response.choices[0].message.content
        print(f"[Worker] Response generated successfully.")
        return answer

    else:
        # Mock / Demo Mode Pipeline
        print(f"[Worker] Running in Mock RAG Pipeline mode (no OPENAI_API_KEY configured)")
        simulated_response = (
            f"[Mock AI Response] Regarding your query: '{query}':\n\n"
            f"Based on Page 12 of 'nodejs.pdf', Node.js operates using a single-threaded event loop with non-blocking I/O. "
            f"This architecture allows it to handle high-concurrency requests with low memory footprint.\n\n"
            f"Reference: Page 12, nodejs.pdf\n"
            f"(Note: To use live OpenAI completions and embeddings, set OPENAI_API_KEY in .env)"
        )

        print(f"[Worker] Simulated context retrieved and response returned.")
        return simulated_response
