import os
import shutil
import requests
import feedparser
import re
from html import unescape
import hashlib

POSTS_DIR = "posts"
LOCAL_FEED_FILE = "feed.atom"  # Your backup Atom feed file path
LIVE_FEED_URL = "https://www.thway.uk/feeds/posts/default"

def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def get_content_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def clear_posts_folder(posts_dir):
    if os.path.exists(posts_dir):
        print(f"Clearing existing posts folder: {posts_dir}")
        shutil.rmtree(posts_dir)
    os.makedirs(posts_dir, exist_ok=True)

def parse_feed(feed):
    posts = []
    for entry in feed.entries:
        title = getattr(entry, 'title', None)
        if not title:
            print("Skipping entry without title")
            continue

        content = None
        if hasattr(entry, 'content'):
            content = entry.content[0].value
        elif hasattr(entry, 'summary'):
            content = entry.summary
        else:
            print(f"Skipping entry '{title}' with no content")
            continue

        content = unescape(content)
        slug = slugify(title)

        # Extract year/month for folder
        if hasattr(entry, 'published'):
            date_folder = entry.published[:7].replace('-', '/')  # e.g. '2023/04'
        elif hasattr(entry, 'updated'):
            date_folder = entry.updated[:7].replace('-', '/')
        else:
            date_folder = ''

        folder_path = os.path.join(POSTS_DIR, date_folder)
        os.makedirs(folder_path, exist_ok=True)

        filename = f"{slug}.html"
        filepath = os.path.join(folder_path, filename)

        posts.append({
            'title': title,
            'content': content,
            'filepath': filepath,
            'relative_url': os.path.join(date_folder, filename).replace('\\','/')  # for links in index
        })
    return posts

def write_post_if_updated(filepath, title, content):
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>"""
    new_hash = get_content_hash(html_template)

    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        existing_hash = get_content_hash(existing_content)
        if existing_hash == new_hash:
            print(f"No changes for {filepath}, skipping update.")
            return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Written/updated post: {filepath}")
    return True

def generate_index(posts_dir):
    all_posts = []
    for root, _, files in os.walk(posts_dir):
        for file in files:
            if file.endswith('.html') and file != 'index.html':
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, posts_dir).replace('\\','/')
                all_posts.append(rel_path)
    all_posts.sort()

    links = '\n'.join(
        f'<li><a href="{post}">{post[:-5].replace("-", " ").replace("/", " > ").title()}</a></li>'
        for post in all_posts
    )

    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Blog Posts Index</title>
</head>
<body>
<h1>Blog Posts</h1>
<ul>
{links}
</ul>
</body>
</html>"""

    index_path = os.path.join(posts_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"Generated index at {index_path}")

def load_local_feed(file_path):
    if not os.path.exists(file_path):
        print(f"Local feed file {file_path} not found.")
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    feed = feedparser.parse(content)
    print(f"Loaded {len(feed.entries)} entries from local feed file.")
    return feed

def fetch_live_feed(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        print(f"Fetched {len(feed.entries)} entries from live feed.")
        return feed
    except Exception as e:
        print(f"Failed to fetch live feed: {e}")
        return None

def main():
    # Clear old posts first
    clear_posts_folder(POSTS_DIR)

    # Bulk import/update from local feed file
    local_feed = load_local_feed(LOCAL_FEED_FILE)
    if local_feed:
        local_posts = parse_feed(local_feed)
        for post in local_posts:
            write_post_if_updated(post['filepath'], post['title'], post['content'])

    # Incremental update from live feed URL
    live_feed = fetch_live_feed(LIVE_FEED_URL)
    if live_feed:
        live_posts = parse_feed(live_feed)
        for post in live_posts:
            write_post_if_updated(post['filepath'], post['title'], post['content'])

    # Generate or update index.html
    generate_index(POSTS_DIR)

if __name__ == "__main__":
    main()
