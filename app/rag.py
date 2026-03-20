from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

vectordb = Chroma(
    persist_directory="app/data/chroma_db",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="executive_intelligence"
)

retriever = vectordb.as_retriever(search_kwargs={"k": 4})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_template("""
You are an analyst.
Answer only from the context below.
If the answer is unclear or unsupported by the context, say that directly.

Question:
{question}

Context:
{context}
""")

def ask_rag(question: str):
    docs = vectordb.similarity_search(
    question + " decision making risk strategy",
    k=4
)
    context = "\n\n".join(doc.page_content for doc in docs)
    chain = prompt | llm
    response = chain.invoke({"question": question, "context": context})
    return {
        "answer": response.content,
        "sources": [doc.metadata for doc in docs]
    }
