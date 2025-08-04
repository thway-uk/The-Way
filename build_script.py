import os
import shutil
import requests
import feedparser
import re
from html import unescape
import hashlib
from datetime import datetime

POSTS_DIR = "posts"
PAGES_DIR = "pages"
INDEX_FILE = "index.html"
LOCAL_FEED_FILE = "feed.atom"
LIVE_FEED_URL = "https://www.thway.uk/feeds/posts/default"

def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def get_content_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def clear_output_folders():
    for folder in [POSTS_DIR, PAGES_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

def fetch_feed():
    try:
        response = requests.get(LIVE_FEED_URL)
        if response.status_code == 200:
            with open(LOCAL_FEED_FILE, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return feedparser.parse(response.text)
    except Exception:
        pass
    return feedparser.parse(LOCAL_FEED_FILE)

def extract_post_type(entry):
    for link in entry.links:
        if '/pages/' in link.href:
            return 'page'
    return 'post'

def save_html(path, title, content):
    html = f"""<html><head><title>{title}</title></head>
<body><h1>{title}</h1>{content}</body></html>"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

def process_entries(feed):
    posts = []
    pages = []
    for entry in feed.entries:
        title = getattr(entry, 'title', None)
        content = getattr(entry, 'content', [{'value': ''}])[0]['value']
        content = unescape(content)
        updated = getattr(entry, 'updated', '')
        post_type = extract_post_type(entry)
        slug = slugify(title)
        
        if post_type == 'page':
            path = os.path.join(PAGES_DIR, f"{slug}.html")
            pages.append((title, path))
        else:
            try:
                dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                dt = datetime.now()
            year = str(dt.year)
            month = f"{dt.month:02d}"
            post_folder = os.path.join(POSTS_DIR, year, month)
            os.makedirs(post_folder, exist_ok=True)
            path = os.path.join(post_folder, f"{slug}.html")
            posts.append((title, path))

        save_html(path, title, content)
    return pages, posts

def generate_index(pages, posts):
    toc = "<html><head><title>Index</title></head><body><h1>Table of Contents</h1>\n"

    toc += "<h2>Pages</h2><ul>\n"
    for title, path in pages:
        rel_path = os.path.relpath(path, '.')
        toc += f'<li><a href="{rel_path}">{title}</a></li>\n'
    toc += "</ul>\n"

    toc += "<h2>Posts</h2><ul>\n"
    for title, path in posts:
        rel_path = os.path.relpath(path, '.')
        toc += f'<li><a href="{rel_path}">{title}</a></li>\n'
    toc += "</ul>\n"

    toc += "</body></html>"
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(toc)

def main():
    clear_output_folders()
    feed = fetch_feed()
    pages, posts = process_entries(feed)
    generate_index(pages, posts)
    print("Site generated successfully.")

if __name__ == "__main__":
    main()
    
