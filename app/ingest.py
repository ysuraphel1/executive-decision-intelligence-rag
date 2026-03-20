from pathlib import Path
from dotenv import load_dotenv
import os

import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

RAW_DIR = Path("app/data/raw")
DB_DIR = "app/data/chroma_db"

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def main():
    client = chromadb.PersistentClient(path=DB_DIR)

    embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-3-small"
    )

    collection = client.get_or_create_collection(
        name="executive_intelligence",
        embedding_function=embedding_fn
    )

    ids = []
    documents = []
    metadatas = []

    for file in RAW_DIR.glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            ids.append(f"{file.stem}_{i}")
            documents.append(chunk)
            metadatas.append({"source": file.name, "chunk": i})

    if not documents:
        print("No .txt files found in app/data/raw")
        return

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Loaded {len(documents)} chunks into Chroma.")

if __name__ == "__main__":
    main()
