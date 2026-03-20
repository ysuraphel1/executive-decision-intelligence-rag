# Executive Decision Intelligence RAG

A Retrieval-Augmented Generation (RAG) application that analyzes how public leaders make strategic decisions using indexed source documents, semantic search, and grounded LLM responses.

This project demonstrates an end-to-end applied GenAI pipeline using Python, LangChain, OpenAI embeddings, ChromaDB vector storage, and a Streamlit chat interface.

---

## Overview

This system allows users to ask questions such as:

- How does Jamie Dimon make decisions under uncertainty?
- How does Satya Nadella approach AI strategy?
- What innovation themes appear in Jensen Huang’s leadership?

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

## Quick Start

Clone the repository:

git clone https://github.com/ysuraphel1/executive-rag-local.git  
cd executive-rag-local

Create a virtual environment:

python3 -m venv .venv  
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Add your OpenAI API key:

echo "OPENAI_API_KEY=your_api_key_here" > .env

Add source documents:

Place `.txt` files inside:

app/data/raw/

Example:

jamie_dimon_risk.txt  
satya_nadella_ai.txt  
jensen_huang_innovation.txt

Ingest documents into the vector database:

cd app  
python ingest.py

Launch the web interface:

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0

---

## Example Queries

How does Jamie Dimon make decisions?  
How does Satya Nadella talk about AI strategy?  
What innovation themes appear in Jensen Huang's leadership?

---

## Project Structure

executive-rag-local/

├── app/  
│   ├── ingest.py  
│   ├── rag.py  
│   ├── main.py  
│   ├── streamlit_app.py  
│   └── data/  
│       ├── raw/  
│       └── chroma_db/  

├── requirements.txt  
├── README.md  
└── .env.example  

---

## Features

Document chunking pipeline  
OpenAI embedding generation  
Chroma vector storage  
Metadata-aware retrieval filtering  
Source-grounded answer generation  
Streamlit chat interface  
Expandable corpus architecture

---

## Limitations

The system only answers questions about leaders included in the indexed dataset.

To expand coverage:

Add additional `.txt` documents to:

app/data/raw/

Then rerun:

cd app  
python ingest.py

---

## Future Improvements

Automatic ingestion from transcripts and interviews  
Named-entity detection for dynamic retrieval filtering  
Hybrid keyword + semantic search  
Conversation memory support  
Cloud deployment with API endpoint

---

## Author

Yonathan Suraphel

Applied AI / Data Systems Portfolio Project
