import os
import json
import requests
from tqdm import tqdm
from urllib.parse import urljoin

# Environment variables
DISCOURSE_API_KEY = os.getenv("DISCOURSE_API_KEY")
DISCOURSE_USERNAME = os.getenv("DISCOURSE_USERNAME")
DISCOURSE_BASE_URL = os.getenv("DISCOURSE_BASE_URL", "https://community.audirvana.com")

HEADERS = {
    "Api-Key": DISCOURSE_API_KEY,
    "Api-Username": DISCOURSE_USERNAME,
    "User-Agent": "AudirvanaSmartSearchBot/1.0",
    "Accept": "application/json"
}

THREADS_PATH = "data/threads.json"
OUTPUT_PATH = "data/threads_with_posts.json"

# Load threads
with open(THREADS_PATH, "r") as f:
    threads = json.load(f)

updated_threads = []

def fetch_posts(thread_id):
    # Try /t/{id}.json
    url = f"{DISCOURSE_BASE_URL}/t/{thread_id}.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data["post_stream"]["posts"][:3]  # First 3 posts
    except Exception as e:
        print(f"❌ Failed /t/{thread_id}.json: {e}")

    # Fallback: /posts.json?topic_id=
    try:
        fallback_url = f"{DISCOURSE_BASE_URL}/posts.json?topic_id={thread_id}"
        r = requests.get(fallback_url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("latest_posts", [])[:3]
    except Exception as e:
        print(f"❌ Fallback failed for thread {thread_id}: {e}")
        return []

# Process threads
for thread in tqdm(threads, desc="Fetching posts"):
    posts = fetch_posts(thread["id"])
    thread["posts"] = posts

    # Fix broken/malformed URLs
    if "url" in thread:
        thread["url"] = urljoin(DISCOURSE_BASE_URL, thread["url"].replace(DISCOURSE_BASE_URL, ""))

    updated_threads.append(thread)

# Save output
os.makedirs("data", exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(updated_threads, f, indent=2)

print(f"\n✅ Done: {len(updated_threads)} threads saved with posts in {OUTPUT_PATH}")
