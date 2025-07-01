import requests
from bs4 import BeautifulSoup
import json
import os
import time
from sentence_transformers import SentenceTransformer

BASE_URL = "https://community.audirvana.com"
MAX_THREADS = 500
OUTPUT_FILE = "data/threads_with_embeddings.json"
os.makedirs("data", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

model = SentenceTransformer('all-MiniLM-L6-v2')

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return text

def get_slug_and_id(href):
    parts = href.strip("/").split("/")
    try:
        slug = parts[-2]
        thread_id = parts[-1]
        return slug, thread_id
    except IndexError:
        return None, None

def fetch_posts(slug, thread_id, max_posts=3):
    url = f"{BASE_URL}/t/{slug}/{thread_id}.json"
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return []
        data = r.json()
        # Clean each post from HTML to plain text here
        cleaned_posts = []
        for post in data["post_stream"]["posts"][:max_posts]:
            cleaned_text = clean_html(post["cooked"])
            cleaned_posts.append(cleaned_text)
        return cleaned_posts
    except Exception as e:
        print(f"Error fetching posts for {slug}/{thread_id}: {e}")
        return []

def fetch_topics_from_html(page=0):
    url = f"{BASE_URL}/latest?page={page}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"HTTP error {response.status_code} on page {page}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        topic_links = soup.select("a.title")
        topics = []
        for link in topic_links:
            title = link.get_text(strip=True)
            href = link['href']
            slug, thread_id = get_slug_and_id(href)
            if not slug or not thread_id:
                continue
            posts = fetch_posts(slug, thread_id)
            combined_text = ' '.join(posts) if posts else ''
            embedding = model.encode(combined_text).tolist() if combined_text else []
            topics.append({
                "id": thread_id,
                "slug": slug,
                "title": title,
                "url": f"{BASE_URL}/t/{slug}/{thread_id}",
                "posts": posts,
                "embedding": embedding
            })
            time.sleep(0.4)  # gentle pause
        return topics
    except Exception as e:
        print(f"Error scraping page {page}: {e}")
        return []

def scrape_all():
    all_threads = []
    page = 0
    while len(all_threads) < MAX_THREADS:
        print(f"Scraping page {page}...")
        threads = fetch_topics_from_html(page)
        if not threads:
            break
        all_threads.extend(threads)
        if len(all_threads) >= MAX_THREADS:
            all_threads = all_threads[:MAX_THREADS]
            break
        page += 1
        time.sleep(1)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_threads, f, indent=2, ensure_ascii=False)
    print(f"{len(all_threads)} threads saved to {OUTPUT_FILE}.")

if __name__ == "__main__":
    scrape_all()

