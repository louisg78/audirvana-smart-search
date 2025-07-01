import numpy as np
from sentence_transformers import SentenceTransformer
import json

with open("data/threads_with_embeddings.json") as f:
    threads = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=20):
    query_vec = model.encode(query)
    results = []
    for thread in threads:
        vec = np.array(thread["embedding"])
        similarity = np.dot(query_vec, vec) / (np.linalg.norm(query_vec) * np.linalg.norm(vec))
        results.append((similarity, thread))
    results.sort(reverse=True, key=lambda x: x[0])
    return [x[1] for x in results[:top_k]]

