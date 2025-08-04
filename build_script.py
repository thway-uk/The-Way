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

def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

def download_feed():
    print("Downloading Atom feed...")
    response = requests.get(LIVE_FEED_URL)
    with open(LOCAL_FEED_FILE, 'wb') as f:
        f.write(response.content)
    print("Feed downloaded.")

def extract_post_type(entry):
    if hasattr(entry, 'tags'):
        for tag in entry.tags:
            if isinstance(tag, dict):
                term = tag.get('term', '').lower()
            else:
                term = getattr(tag, 'term', tag).lower()
            if term == 'page':
                return 'page'
    return 'post'

def extract_labels(entry):
    labels = []
    if hasattr(entry, 'tags'):
        for tag in entry.tags:
            if isinstance(tag, dict):
                term = tag.get('term')
            else:
                term = getattr(tag, 'term', tag)
            if term.lower() not in ('page', 'post'):
                labels.append(slugify(term))
    return labels

def process_entries(feed):
    pages = []
    posts = []

    for entry in feed.entries:
        title = getattr(entry, 'title', 'Untitled')
        content = entry.content[0].value if 'content' in entry else entry.summary
        published = entry.published if 'published' in entry else ''
        post_type = extract_post_type(entry)
        labels = extract_labels(entry)
        slug = slugify(title)
        date = datetime.strptime(published[:10], '%Y-%m-%d') if published else None

        post_data = {
            'title': unescape(title),
            'content': content,
            'slug': slug,
            'labels': labels,
            'date': date,
        }

        if post_type == 'page':
            pages.append(post_data)
        else:
            posts.append(post_data)

    return pages, posts

def save_post(post, base_dir):
    subdir = base_dir
    if post['date']:
        year = str(post['date'].year)
        month = str(post['date'].month).zfill(2)
        subdir = os.path.join(base_dir, year, month)
    os.makedirs(subdir, exist_ok=True)
    file_path = os.path.join(subdir, f"{post['slug']}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(post['content'])
    return os.path.relpath(file_path, base_dir)

def generate_index(pages, posts):
    toc = "<h1>Table of Contents</h1>\n<h2>Pages</h2><ul>\n"
    for page in pages:
        path = save_post(page, PAGES_DIR)
        toc += f"<li><a href='{PAGES_DIR}/{path}'>{page['title']}</a></li>\n"
    toc += "</ul>\n<h2>Posts</h2><ul>\n"
    for post in posts:
        path = save_post(post, POSTS_DIR)
        toc += f"<li><a href='{POSTS_DIR}/{path}'>{post['title']}</a></li>\n"
    toc += "</ul>"

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(f"<html><body>{toc}</body></html>")

def main():
    clear_folder(POSTS_DIR)
    clear_folder(PAGES_DIR)
    download_feed()

    feed = feedparser.parse(LOCAL_FEED_FILE)
    print(f"Found {len(feed.entries)} entries in feed.")
    pages, posts = process_entries(feed)
    print(f"{len(pages)} pages, {len(posts)} posts.")
    generate_index(pages, posts)
    print(f"Index and posts saved successfully.")

if __name__ == "__main__":
    main()
