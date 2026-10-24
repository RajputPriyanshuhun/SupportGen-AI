"""
[SupportGen-AI] Pure NumPy Vector Store & Cosine Similarity Engine
100% Original, Self-Authored Code for IIT Guwahati GenAI Capstone.
Performs fast vector retrieval and similarity matching using pure NumPy.
"""

import numpy as np
import json
from pathlib import Path

class NumPyVectorStore:
    def __init__(self, store_path: str = "data/vector_store.json"):
        self.store_path = Path(store_path)
        self.vectors = None
        self.metadata = []

    def cosine_similarity(self, query_vector: np.ndarray, doc_vectors: np.ndarray) -> np.ndarray:
        """Computes pure NumPy cosine similarity between query and document vectors."""
        # Dot product divided by the product of norms
        dot_product = np.dot(doc_vectors, query_vector)
        query_norm = np.linalg.norm(query_vector)
        doc_norms = np.linalg.norm(doc_vectors, axis=1)
        
        # Avoid division by zero
        safe_norms = np.where((doc_norms * query_norm) == 0, 1e-10, (doc_norms * query_norm))
        return dot_product / safe_norms

    def add_embeddings(self, embeddings: list, chunks: list):
        """Stores vectors and their corresponding text metadata."""
        self.vectors = np.array(embeddings, dtype=np.float32)
        self.metadata = chunks
        print(f"✅ Stored {len(chunks)} vectors in NumPy Vector Store successfully!")

    def search(self, query_vector: list, top_k: int = 3) -> list:
        """Searches the top-k most similar chunks using cosine similarity."""
        if self.vectors is None or len(self.vectors) == 0:
            print("⚠️ Vector store is empty!")
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        scores = self.cosine_similarity(q_vec, self.vectors)
        
        # Get top-k indices sorted by highest similarity score
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "score": float(scores[idx]),
                "chunk": self.metadata[idx]
            })
        return results

if __name__ == "__main__":
    # Quick test of the NumPy vector engine
    store = NumPyVectorStore()
    # Dummy mock vectors for testing pipeline integrity
    mock_embeddings = [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7], [0.1, 0.2, 0.4]]
    mock_chunks = [
        {"source": "test_policy.md", "section": "Returns", "text": "Return window is 7 days."},
        {"source": "test_policy.md", "section": "Refunds", "text": "Refunds are processed in 3 days."},
        {"source": "test_policy.md", "section": "Shipping", "text": "Standard shipping takes 5 days."}
    ]
    
    store.add_embeddings(mock_embeddings, mock_chunks)
    query = [0.1, 0.2, 0.35]
    results = store.search(query, top_k=2)
    
    print("\n🔍 Test Search Results:")
    for res in results:
        print(f"Score: {res['score']:.4f} | Section: {res['chunk']['section']} | Text: {res['chunk']['text']}")