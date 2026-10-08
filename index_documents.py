import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        print("❌ OPENAI_API_KEY is not configured in .env. Indexing requires an active OpenAI API key for embeddings.")
        return

    # Check for PDF file in local directory or parent rag folder
    possible_paths = [
        BASE_DIR / "nodejs.pdf",
        BASE_DIR.parent / "rag" / "nodejs.pdf"
    ]

    pdf_path = None
    for p in possible_paths:
        if p.exists():
            pdf_path = p
            break

    if not pdf_path:
        print("❌ Could not find 'nodejs.pdf' to index.")
        return

    print(f"📖 Loading PDF from: {pdf_path}")
    loader = PyPDFLoader(file_path=str(pdf_path))
    docs = loader.load()
    print(f"📄 Loaded {len(docs)} pages.")

    print("✂️ Splitting document into text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400
    )
    chunks = text_splitter.split_documents(documents=docs)
    print(f"🧩 Created {len(chunks)} text chunks.")

    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection_name = os.getenv("QDRANT_COLLECTION", "learning_rag")

    print(f"🚀 Generating embeddings with text-embedding-3-large and saving to Qdrant collection '{collection_name}' at {qdrant_url}...")
    embedding_model = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=api_key
    )

    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        url=qdrant_url,
        collection_name=collection_name
    )
    print(f"✅ Indexing complete! Collection '{collection_name}' is ready in Qdrant.")


if __name__ == "__main__":
    main()
