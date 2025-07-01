import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://community.audirvana.com"
MAX_THREADS = 500
OUTPUT_FILE = "data/threads.json"
os.makedirs("data", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0"
}

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
        return [post["cooked"] for post in data["post_stream"]["posts"][:max_posts]]
    except:
        return []

def fetch_topics_from_html(page=0):
    url = f"{BASE_URL}/latest?page={page}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} sur la page {page}")
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
            topics.append({
                "id": thread_id,
                "slug": slug,
                "title": title,
                "url": f"{BASE_URL}/t/{slug}/{thread_id}",
                "posts": posts
            })
            time.sleep(0.4)  # douce pause pour éviter blocage
        return topics
    except Exception as e:
        print(f"Erreur lors du scraping : {e}")
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
    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_threads, f, indent=2)
    print(f"{len(all_threads)} threads sauvegardés dans {OUTPUT_FILE}.")

if __name__ == "__main__":
    scrape_all()

