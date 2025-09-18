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
2. Run your local LLM (Ollama or other). Make note of the HTTP endpoint.
3. Start Streamlit:
4. In the sidebar, set the LLM endpoint (e.g. `http://localhost:11434/generate`) and model name (if required).
5. Upload PDF/XLSX files → `Process & Index` → Ask questions.

## How it works
1. Documents are parsed (pdfplumber/pandas).
2. Text is chunked and embedded with `sentence-transformers`.
3. Embeddings are stored in FAISS.
4. On query, top-k chunks retrieved are fed to local LLM with the prompt.

## Notes & improvements
- For scanned PDFs enable OCR via `pytesseract`.
- For more robust table extraction, try `camelot` or `tabula-py`.
- For larger datasets, persist FAISS index to disk and use advanced index types.
- Secure local LLM endpoint if exposing beyond localhost.

## License
MIT

