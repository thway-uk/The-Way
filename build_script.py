import os
import requests
import feedparser
import re
from html import unescape

ATOM_FEED_URL = "https://www.thway.uk/feeds/posts/default"
POSTS_DIR = "posts"

os.makedirs(POSTS_DIR, exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def parse_feed_and_create_posts():
    response = requests.get(ATOM_FEED_URL)
    feed = feedparser.parse(response.content)

    for entry in feed.entries:
        title = entry.title
        content = entry.content[0].value if 'content' in entry else entry.summary
        content = unescape(content)

        slug = slugify(title)
        filename = f"{slug}.html"
        filepath = os.path.join(POSTS_DIR, filename)

        html_content = f"""<!DOCTYPE html>
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

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Created {filepath}")

if __name__ == "__main__":
    parse_feed_and_create_posts()
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Created {filepath}")

if __name__ == "__main__":
    parse_feed_and_create_posts()
