import os
import re
import feedparser
from urllib.parse import urlparse
from datetime import datetime

FEED_FILE = "feed.atom"
OUTPUT_DIR = "output"

def slugify(url):
    path = urlparse(url).path
    return path.rstrip('/').split('/')[-1] or "index"

def extract_date_path(url):
    match = re.search(r'/(\d{4})/(\d{2})/', url)
    return match.groups() if match else (None, None)

def write_html(path, title, date, content):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: auto; padding: 2em; }}
    h1 {{ color: #333; }}
    a {{ color: #0066cc; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p><em>{date}</em></p>
  <div>{content}</div>
</body>
</html>
""")

def main():
    feed = feedparser.parse(FEED_FILE)
    posts = []
    pages = []

    for entry in feed.entries:
        url = entry.link
        title = entry.title
        content = entry.get("content", [{}])[0].get("value") or entry.get("summary", "")
        date = entry.get("published", entry.get("updated", ""))
        date_obj = datetime.strptime(date[:10], "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")

        year, month = extract_date_path(url)
        slug = slugify(url)

        if year and month:
            rel_path = f"{year}/{month}/{slug}"
            out_path = os.path.join(OUTPUT_DIR, rel_path)
            posts.append((title, rel_path, formatted_date))
        else:
            rel_path = f"pages/{slug}"
            out_path = os.path.join(OUTPUT_DIR, rel_path)
            pages.append((title, rel_path, formatted_date))

        write_html(out_path, title, formatted_date, content)

    # Write the TOC index.html
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Table of Contents</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; max-width: 800px; margin: auto; padding: 2em; }
    h1, h2 { color: #333; }
    ul { padding-left: 1.5em; }
    li { margin-bottom: 0.5em; }
  </style>
</head>
<body>
  <h1>Table of Contents</h1>
""")

        if posts:
            f.write("<h2>Blog Posts</h2><ul>\n")
            for title, path, date in sorted(posts, key=lambda x: x[2], reverse=True):
                f.write(f'<li><a href="{path}/">{title}</a> — {date}</li>\n')
            f.write("</ul>\n")

        if pages:
            f.write("<h2>Pages</h2><ul>\n")
            for title, path, date in sorted(pages, key=lambda x: x[2]):
                f.write(f'<li><a href="{path}/">{title}</a> — {date}</li>\n')
            f.write("</ul>\n")

        f.write("</body></html>")

if __name__ == "__main__":
    main()
