import os
import re
import shutil
import requests
import feedparser
from datetime import datetime

ATOM_FEED_URL = "https://www.thway.uk/feeds/posts/default?alt=atom"
OUTPUT_DIR = "site"
POSTS_DIR = os.path.join(OUTPUT_DIR, "posts")
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
ATOM_FILE = "feed.atom"

def download_atom_feed():
    print("Downloading Atom feed...")
    response = requests.get(ATOM_FEED_URL)
    if response.status_code == 200:
        with open(ATOM_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Feed downloaded.")
    else:
        print("Failed to download feed:", response.status_code)

def clear_output_directory():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(PAGES_DIR, exist_ok=True)

def slugify(title):
    return re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')

def extract_post_type(entry):
    if 'category' in entry:
        for cat in entry.category:
            if cat.term.lower() == 'page':
                return 'page'
    if 'labels' in entry:
        for label in entry.labels:
            if label.lower() == 'page':
                return 'page'
    if 'title' in entry and 'Page' in entry.title:
        return 'page'
    return 'post'

def save_html(path, title, content):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    {content}
</body>
</html>"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def process_entries(feed):
    posts = []
    pages = []
    print(f"Found {len(feed.entries)} entries in feed.")
    for entry in feed.entries:
        title = getattr(entry, 'title', 'Untitled')
        content = getattr(entry, 'content', [{'value': ''}])[0]['value']
        updated = getattr(entry, 'updated', '')
        post_type = extract_post_type(entry)
        slug = slugify(title)

        print(f"Processing: {title} (Type: {post_type})")

        if post_type == 'page':
            path = os.path.join(PAGES_DIR, f"{slug}.html")
            pages.append((title, os.path.relpath(path, OUTPUT_DIR)))
        else:
            try:
                dt = datetime.strptime(updated, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                dt = datetime.now()
            year = str(dt.year)
            month = f"{dt.month:02d}"
            post_folder = os.path.join(POSTS_DIR, year, month)
            path = os.path.join(post_folder, f"{slug}.html")
            posts.append((title, os.path.relpath(path, OUTPUT_DIR)))

        save_html(path, title, content)
    return pages, posts

def create_index(pages, posts):
    toc = "<h1>Table of Contents</h1><ul>"
    if pages:
        toc += "<li><strong>Pages</strong><ul>"
        for title, path in pages:
            toc += f'<li><a href="{path}">{title}</a></li>'
        toc += "</ul></li>"
    if posts:
        toc += "<li><strong>Posts</strong><ul>"
        for title, path in posts:
            toc += f'<li><a href="{path}">{title}</a></li>'
        toc += "</ul></li>"
    toc += "</ul>"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Index</title>
</head>
<body>
    {toc}
</body>
</html>"""

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    download_atom_feed()
    clear_output_directory()
    feed = feedparser.parse(ATOM_FILE)
    pages, posts = process_entries(feed)
    create_index(pages, posts)
    print("Done.")

if __name__ == "__main__":
    main()
    
