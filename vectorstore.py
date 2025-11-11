import os
import pickle
from sentence_transformers import SentenceTransformer
import numpy as np
try:
    import faiss
except Exception:
    faiss = None

class VectorStore:
    def __init__(self, model_name, index_path, doc_store_path):
        self.model = SentenceTransformer(model_name)
        self.index_path = index_path
        self.doc_store_path = doc_store_path
        self.doc_store = {}  

        if faiss is None:
            raise RuntimeError('faiss not available; install faiss-cpu')

        if os.path.exists(index_path) and os.path.exists(doc_store_path):
            self._load()
        else:
            self.index = None

    def _load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.doc_store_path, 'rb') as f:
            self.doc_store = pickle.load(f)

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        os.makedirs(os.path.dirname(self.doc_store_path), exist_ok=True)
        with open(self.doc_store_path, 'wb') as f:
            pickle.dump(self.doc_store, f)

    def add_documents(self, docs):
        texts = [d[1] for d in docs]
        ids = [d[0] for d in docs]
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))

        self.index.add_with_ids(embeddings, np.array(ids, dtype='int64'))

        for d in docs:
            self.doc_store[d[0]] = {'text': d[1], 'meta': d[2]}

        self._save()

    def query(self, query_text, top_k=5):
        if self.index is None:
            return []
        q_emb = self.model.encode([query_text], convert_to_numpy=True)
        D, I = self.index.search(q_emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if int(idx) == -1:
                continue
            doc = self.doc_store.get(int(idx))
            if doc:
                results.append({
                    'id': int(idx),                
                    'score': float(score),         
                    'text': doc['text'],
                    'meta': doc['meta']
                })
        return results
