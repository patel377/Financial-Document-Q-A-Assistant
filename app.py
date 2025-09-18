# app.py
import streamlit as st
from processing import extract_from_pdf, extract_from_excel
from indexing import DocumentIndex
from llm_client import ask_llm
import os
from utils import save_uploaded_file, readable_file_size

st.set_page_config(page_title="Financial Doc Q&A", layout="wide")
st.title("Financial Document Q&A Assistant")

# Sidebar: settings
with st.sidebar.expander("Settings"):
    st.write("Local LLM endpoint (e.g., Ollama):")
    llm_endpoint = st.text_input("LLM endpoint URL", value="http://localhost:11434/generate")
    model_name = st.text_input("Model name (if required by your endpoint)", value="your-model")
    top_k = st.number_input("Retrieval top_k", min_value=1, max_value=10, value=4)
    chunk_size = st.number_input("Chunk size (chars)", min_value=200, max_value=2000, value=800)
    chunk_overlap = st.number_input("Chunk overlap (chars)", min_value=0, max_value=500, value=100)

st.session_state.setdefault("index", None)
st.session_state.setdefault("documents", [])
st.session_state.setdefault("chat_history", [])

# File uploader
st.subheader("Upload financial documents (PDF / Excel)")
uploaded_files = st.file_uploader("Upload one or more files", accept_multiple_files=True, type=["pdf","xls","xlsx"])

if uploaded_files:
    if st.button("Process & Index"):
        with st.spinner("Extracting and indexing documents..."):
            index = DocumentIndex(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))
            for uf in uploaded_files:
                # Save file to temp folder
                saved_path = save_uploaded_file(uf)
                filesize = os.path.getsize(saved_path)
                st.write(f"Processing **{uf.name}** — {readable_file_size(filesize)}")
                if uf.type == "application/pdf" or uf.name.lower().endswith(".pdf"):
                    extracted = extract_from_pdf(saved_path, ocr=False)  # set ocr=True if scanned PDFs
                else:
                    extracted = extract_from_excel(saved_path)
                # extracted: list of dicts [{ "text": ..., "meta": {file, page, table}}]
                index.add_document_chunks(extracted, source_meta={"filename": uf.name})
                st.success(f"Indexed {uf.name}")
            # finalize
            index.build_index()
            st.session_state.index = index
            st.success("Index built. Ask questions in the chat box below.")

# Chat interface
st.subheader("Ask questions about the uploaded documents")
query = st.text_input("Your question", key="user_query")
if st.button("Ask") and query:
    if st.session_state.index is None:
        st.warning("No documents indexed yet. Upload files and press 'Process & Index'.")
    else:
        with st.spinner("Retrieving context and generating answer..."):
            index: DocumentIndex = st.session_state.index
            retrieved = index.retrieve(query, top_k=int(top_k))
            # Build prompt
            context_text = "\n\n---\n\n".join([f"[Source: {r['meta'].get('filename','unknown')} | page:{r['meta'].get('page','?')}]\n{r['text']}" for r in retrieved])
            prompt = f"""You are a financial-document assistant. Use only the following extracted document text to answer the user. If the answer is not contained, say you don't know.

Context:
{context_text}

User question:
{query}

Provide a concise answer and cite which sources (filename and page) you used."""
            response = ask_llm(prompt=prompt, llm_endpoint=llm_endpoint, model=model_name, max_tokens=512)
            st.session_state.chat_history.append({"query": query, "response": response, "retrieved": retrieved})
            # Display
            st.markdown("**Answer:**")
            st.write(response)
            with st.expander("Show retrieved context"):
                for r in retrieved:
                    st.markdown(f"- **{r['meta'].get('filename','?')}** | page: {r['meta'].get('page','?')} — snippet:")
                    st.write(r['text'][:800] + ("..." if len(r['text'])>800 else ""))

# Show chat history
if st.session_state.chat_history:
    st.subheader("Conversation history")
    for i, turn in enumerate(reversed(st.session_state.chat_history[-10:])):
        st.markdown(f"**Q:** {turn['query']}")
        st.markdown(f"**A:** {turn['response']}")
        st.write("---")
