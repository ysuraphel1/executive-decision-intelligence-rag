from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

BASE_DIR = Path(__file__).parent
DB_DIR = str(BASE_DIR / "data" / "chroma_db")

_vectordb: Chroma | None = None


def get_vectordb() -> Chroma:
    global _vectordb
    if _vectordb is None:
        _vectordb = Chroma(
            persist_directory=DB_DIR,
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
            collection_name="executive_intelligence",
        )
    return _vectordb


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template(
    """You are an executive strategy analyst. Answer the question below using ONLY the provided context.
Be specific: quote or paraphrase the source material directly where relevant.
If the context does not contain enough information to answer, say so clearly.

Question: {question}

Context:
{context}

Answer:"""
)


def ask_rag(question: str, leader: str | None = None) -> dict:
    """
    Query the vector store and generate a grounded answer.

    Args:
        question: The user's question.
        leader: Optional leader name to restrict retrieval (e.g. "Jamie Dimon").
    """
    db = get_vectordb()

    search_kwargs: dict = {"k": 5}
    if leader:
        search_kwargs["filter"] = {"leader": leader}

    docs = db.similarity_search(question, **search_kwargs)

    if not docs:
        return {
            "answer": "No relevant source material was found. Make sure the database has been ingested by running `python app/ingest.py`.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    chain = prompt | llm
    response = chain.invoke({"question": question, "context": context})

    sources = []
    seen = set()
    for doc in docs:
        key = (doc.metadata.get("source", ""), doc.metadata.get("chunk", ""))
        if key not in seen:
            seen.add(key)
            sources.append(doc.metadata)

    return {"answer": response.content, "sources": sources}
