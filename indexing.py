# indexing.py
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from tqdm import tqdm
import math

class DocumentIndex:
    def __init__(self, chunk_size=800, chunk_overlap=100, embedding_model_name="all-MiniLM-L6-v2"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embed_model = SentenceTransformer(embedding_model_name)
        self.texts = []   # list of text chunks
        self.meta = []    # metadata dicts for each chunk
        self.embeddings = None
        self.index = None

    def _chunk_text(self, text):
        chunks = []
        start = 0
        L = len(text)
        while start < L:
            end = min(L, start + self.chunk_size)
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap
            if start < 0:
                start = 0
            if start >= L:
                break
        return chunks

    def add_document_chunks(self, extracted_list, source_meta=None):
        """
        extracted_list: list of dicts [{"text":..., "meta": {...}}]
        source_meta: e.g. {"filename": "abc.pdf"}
        """
        for block in extracted_list:
            text = block.get("text","").strip()
            if not text:
                continue
            block_meta = block.get("meta",{}).copy()
            if source_meta:
                block_meta.update(source_meta)
            chunks = self._chunk_text(text)
            for c in chunks:
                self.texts.append(c)
                self.meta.append(block_meta)

    def build_index(self):
        if not self.texts:
            raise ValueError("No texts to index")
        # compute embeddings in batches
        embs = self.embed_model.encode(self.texts, show_progress_bar=True, convert_to_numpy=True)
        self.embeddings = embs.astype("float32")
        dim = self.embeddings.shape[1]
        # build FAISS index
        self.index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized vectors; simpler IP
        # normalize embeddings
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

    def retrieve(self, query, top_k=4):
        q_emb = self.embed_model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, top_k)
        results = []
        for i in range(len(I[0])):
            idx = int(I[0][i])
            score = float(D[0][i])
            results.append({"text": self.texts[idx], "meta": self.meta[idx], "score": score})
        return results
