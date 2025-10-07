import os
from threading import RLock

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingIndex:

    def __init__(self, path="data/faiss.index", meta_path="data/faiss.meta.npy"):
        self.path = path
        self.meta_path = meta_path
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.lock = RLock()

        self.dim = 384
        self.index = faiss.IndexFlatL2(self.dim)
        self.meta = []

        self._load()

    def _load(self):
        if os.path.exists(self.path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.path)
            self.meta = list(np.load(self.meta_path))

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        faiss.write_index(self.index, self.path)
        np.save(self.meta_path, np.array(self.meta, dtype=np.int64), allow_pickle=False)

    def embed(self, texts):
        emb = self.model.encode(texts, normalize_embeddings=True)
        return np.array(emb).astype("float32")

    def add(self, prompt_id: int, text: str):
        with self.lock:
            vec = self.embed([text])
            self.index.add(vec)
            self.meta.append(prompt_id)
            self._save()

    def search(self, query: str, k=5):
        with self.lock:
            if self.index.ntotal == 0:
                return []

        q = self.embed([query])
        D, I = self.index.search(q, k)
        result_ids = [self.meta[i] for i in I[0] if i >= 0]
        return result_ids


embedding_index = EmbeddingIndex()
