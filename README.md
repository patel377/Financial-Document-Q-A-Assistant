# Financial Document Q&A Assistant

A local Streamlit app that extracts financial data from PDF and Excel files and provides an interactive question-answering interface backed by a local Small Language Model (SLM) such as Ollama.

## Features
- Upload PDFs and Excel files (income statements, balance sheets, cash flows).
- Extract text and tables, handle OCR for scanned PDFs (optional).
- Build a local vector index (FAISS) using sentence-transformers embeddings.
- Ask natural language queries — retrieval-augmented generation with a local LLM.
- Local-only deployment (no cloud required).

## Requirements
See `requirements.txt`. Tested with Python 3.10+.

## Quick start
1. Create virtualenv and install dependencies:
