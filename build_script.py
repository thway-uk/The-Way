import os
import re
import requests
import hashlib
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime

FEED_URL = 'https://your-blog.blogspot.com/feeds/posts/default?alt=atom'
OUTPUT_DIR = 'posts'

def slugify(title):
    return re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-') + '.html'

def download_feed():
    print("Downloading Atom feed...")
    response = requests.get(FEED_URL)
    response.raise_for_status()
    with open("feed.atom", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Feed downloaded.")
    return "feed.atom"

def parse_and_save_posts(atom_file):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    feed = feedparser.parse(atom_file)
    print(f"Found {len(feed.entries)} entries in feed.")
    for entry in feed.entries:
        title = entry.get('title', 'Untitled')
        content = entry.get('content', [{'value': ''}])[0]['value']
        post_id = slugify(title)

        # Optional: add date if you want
        pub_date = entry.get('published', '')
        pub_date = datetime.strptime(pub_date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d %b %Y') if pub_date else ''

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <p><em>{pub_date}</em></p>
    <div>{content}</div>
    <p><a href="../index.html">Back to Index</a></p>
</body>
</html>"""

        with open(os.path.join(OUTPUT_DIR, post_id), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {post_id}")

def generate_index(atom_file):
    feed = feedparser.parse(atom_file)
    links = []
    for entry in feed.entries:
        title = entry.get('title', 'Untitled')
        post_id = slugify(title)
        links.append(f'<li><a href="posts/{post_id}">{title}</a></li>')

    index_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Blog Index</title>
</head>
<body>
    <h1>Blog Posts</h1>
    <ul>
        {''.join(links)}
    </ul>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("Index page generated.")

def main():
    atom_file = download_feed()
    parse_and_save_posts(atom_file)
    generate_index(atom_file)

if __name__ == "__main__":
    main()
