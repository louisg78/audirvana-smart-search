import numpy as np
from sentence_transformers import SentenceTransformer
import json

with open("data/threads_with_embeddings.json", encoding="utf-8") as f:
    threads = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Precompute normalized embeddings for threads
for thread in threads:
    emb = np.array(thread["embedding"])
    norm = np.linalg.norm(emb)
    thread["embedding_norm"] = emb / norm if norm > 0 else emb

def search(query, top_k=20):
    query_vec = model.encode(query)
    query_vec = query_vec / np.linalg.norm(query_vec)
    
    results = []
    for thread in threads:
        emb_norm = thread.get("embedding_norm")
        if emb_norm is None:
            continue
        similarity = np.dot(query_vec, emb_norm)
        results.append((similarity, thread))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in results[:top_k]]

