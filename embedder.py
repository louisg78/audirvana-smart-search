import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

INPUT_FILE = "data/threads_with_posts.json"
OUTPUT_FILE = "data/threads_with_embeddings.json"

def load_threads():
    with open(INPUT_FILE, "r") as f:
        return json.load(f)

def save_threads(threads):
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(threads, f, indent=2)

def main():
    threads = load_threads()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    for thread in threads:
        post_texts = []
        for post in thread.get("posts", []):
            # Use cooked HTML content if it's a dict (as expected)
            if isinstance(post, dict) and "cooked" in post:
                post_texts.append(post["cooked"])
            elif isinstance(post, str):  # fallback if it's already a string
                post_texts.append(post)
        
        full_text = thread["title"] + " " + " ".join(post_texts)
        embedding = model.encode(full_text)
        thread["embedding"] = embedding.tolist()

    save_threads(threads)
    print(f"✅ Saved {len(threads)} threads with embeddings to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

