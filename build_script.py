import os
import re
import feedparser
from urllib.parse import urlparse
from html import unescape

FEED_FILE = "feed.atom"
OUTPUT_DIR = "site"

def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-') or "index"

def extract_date_from_url(url):
    match = re.search(r'/(\d{4})/(\d{2})/', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def write_html(folder_path, title, content):
    os.makedirs(folder_path, exist_ok=True)
    filepath = os.path.join(folder_path, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding: 2em; }}
h1 {{ color: #222; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div>{content}</div>
</body>
</html>""")

def main():
    feed = feedparser.parse(FEED_FILE)
    posts = []
    pages = []

    for entry in feed.entries:
        title = getattr(entry, "title", "Untitled")
        content = ""
        if hasattr(entry, "content"):
            content = unescape(entry.content[0].value)
        elif hasattr(entry, "summary"):
            content = unescape(entry.summary)
        else:
            content = ""

        url = entry.link
        year, month = extract_date_from_url(url)
        slug = slugify(url.rstrip('/').split('/')[-1])

        if year and month:
            folder_path = os.path.join(OUTPUT_DIR, year, month, slug)
            posts.append((title, f"{year}/{month}/{slug}/"))
        else:
            folder_path = os.path.join(OUTPUT_DIR, "pages", slug)
            pages.append((title, f"pages/{slug}/"))

        write_html(folder_path, title, content)

    # Create index.html with all links
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Table of Contents</title></head>
<body>
<h1>Table of Contents</h1>
""")
        if pages:
            f.write("<h2>Pages</h2><ul>\n")
            for title, href in sorted(pages):
                f.write(f'<li><a href="{href}">{title}</a></li>\n')
            f.write("</ul>\n")

        if posts:
            f.write("<h2>Posts</h2><ul>\n")
            for title, href in sorted(posts, reverse=True):
                f.write(f'<li><a href="{href}">{title}</a></li>\n')
            f.write("</ul>\n")

        f.write("</body></html>")

if __name__ == "__main__":
    main()
