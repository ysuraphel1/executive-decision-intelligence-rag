from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
DB_DIR = str(BASE_DIR / "data" / "chroma_db")

def _leader_from_stem(stem: str) -> str:
    """Derive a display name from a filename stem.

    Expects filenames like  first_last_company.txt  or  first_last.txt.
    Takes the first two underscore-separated tokens and title-cases them.
    Falls back to the whole stem if there is only one token.
    """
    parts = stem.split("_")
    if len(parts) >= 2:
        return " ".join(p.capitalize() for p in parts[:2])
    return stem.replace("_", " ").title()


def load_documents() -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = []
    for file in sorted(RAW_DIR.glob("*.txt")):
        text = file.read_text(encoding="utf-8")
        leader = _leader_from_stem(file.stem)
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={"source": file.name, "leader": leader, "chunk": i},
                )
            )
    return docs


def main():
    docs = load_documents()
    if not docs:
        print(f"No .txt files found in {RAW_DIR}")
        return

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Delete existing collection so re-ingestion is idempotent
    import chromadb
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection("executive_intelligence")
    except Exception:
        pass

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=DB_DIR,
        collection_name="executive_intelligence",
    )

    print(f"Ingested {len(docs)} chunks from {RAW_DIR} into {DB_DIR}")
    leaders = sorted({d.metadata["leader"] for d in docs})
    print(f"Leaders indexed: {', '.join(leaders)}")


if __name__ == "__main__":
    main()
