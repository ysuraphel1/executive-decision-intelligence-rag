# Executive Decision Intelligence RAG

A Retrieval-Augmented Generation (RAG) application that analyzes how public leaders make strategic decisions using indexed source documents, semantic search, and grounded LLM responses.

This project demonstrates an end-to-end applied AI pipeline using Python, LangChain, OpenAI embeddings, Chroma vector search, and a Streamlit chat interface.

---

## Overview

This system allows users to ask questions such as:

- How does Jamie Dimon approach risk?
- How does Satya Nadella think about AI strategy?
- What themes appear in Jensen Huang’s innovation decisions?

The application retrieves relevant source material from an indexed document corpus and generates answers grounded strictly in retrieved context.

---

## Architecture

User Question  
→ Embedding generation  
→ Vector similarity search (ChromaDB)  
→ Metadata filtering by leader  
→ Context retrieval  
→ LLM answer generation (OpenAI)  
→ Source-cited response in Streamlit UI

---

## Tech Stack

Python  
LangChain  
OpenAI API (embeddings + chat model)  
ChromaDB (vector database)  
Streamlit (client interface)  
GitHub Codespaces (development environment)

---

## Project Structure

app/
    ingest.py
    rag.py
    main.py
    streamlit_app.py
    data/
        raw/
        chroma_db/

README.md
requirements.txt

---

## Setup Instructions

Clone repository:

cat > README.md <<'EOF'
# Executive Decision Intelligence RAG

A Retrieval-Augmented Generation (RAG) application that analyzes how public leaders make strategic decisions using indexed source documents, semantic search, and grounded LLM responses.

## Overview

This project demonstrates an end-to-end AI pipeline that:

- Ingests leadership commentary from text sources
- Chunks documents into embeddings
- Stores vectors in ChromaDB
- Retrieves relevant context using semantic search
- Generates grounded answers with OpenAI models
- Serves responses through a Streamlit web interface

Example questions:

- How does Jamie Dimon make decisions?
- How does Satya Nadella approach AI strategy?
- What innovation themes appear in Jensen Huang’s leadership?

## Tech Stack

Python  
LangChain  
OpenAI API (embeddings + chat model)  
ChromaDB (vector database)  
Streamlit (client interface)  
GitHub Codespaces (development environment)

## Project Structure

app/
  ingest.py
  rag.py
  main.py
  streamlit_app.py
  data/
    raw/
    chroma_db/

README.md
requirements.txt

## Setup Instructions

Clone repo:

git clone <your_repo_url>
cd executive-rag-local

Create environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Create .env file:

OPENAI_API_KEY=your_api_key_here

Add text files to:

app/data/raw/

Then ingest:

cd app
python ingest.py

Run CLI:

python main.py

Run web app:

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

## Features

Document chunking pipeline  
Embedding-based retrieval  
Metadata filtering by leader  
Source-grounded responses  
Streamlit chat interface  
Expandable corpus architecture

## Limitations

The system only answers questions about leaders included in the indexed dataset.

To expand coverage, add additional documents to:

app/data/raw/

Then rerun:

python ingest.py

## Future Improvements

Automatic ingestion from transcripts and interviews  
Hybrid keyword + semantic retrieval  
Conversation memory support  
Cloud deployment with API endpoint

## Author

Yonathan Suraphel

Applied AI / Data Systems Portfolio Project
