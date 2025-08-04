import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

# Paths
FEED_FILE = "feed.atom"
OUTPUT_DIR = "site"
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
POSTS_DIR = os.path.join(OUTPUT_DIR, "posts")

# Create base folders
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

# Load Atom feed
tree = ET.parse(FEED_FILE)
root = tree.getroot()
ns = {'atom': 'http://www.w3.org/2005/Atom'}

index_links = []

for entry in root.findall("atom:entry", ns):
    title = entry.find("atom:title", ns).text
    content = entry.find("atom:content", ns).text
    link = entry.find("atom:link", ns).attrib.get("href")

    # Create slug from title
    slug = re.sub(r"[^\w\-]", "-", title.lower()).strip("-")

    # Extract year, month, day from URL (example URL: https://example.com/2025/08/04/post-title/)
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
    if not date_match:
        print(f"Skipping entry '{title}' due to missing date in URL")
        continue
    year, month, day = date_match.groups()

    # Build output directory for this post
    post_dir = os.path.join(POSTS_DIR, year, month)
    os.makedirs(post_dir, exist_ok=True)

    # Output HTML file path
    output_file = os.path.join(post_dir, f"{slug}.html")

    # Write a simple HTML page
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    <div>{content}</div>
    <p><a href="../../index.html">Back to index</a></p>
</body>
</html>"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Prepare link for index (relative to index.html)
    relative_path = f"posts/{year}/{month}/{slug}.html"
    index_links.append(f'<li><a href="{relative_path}">{title} ({year}-{month}-{day})</a></li>')

# Generate index.html listing all posts
index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Blog Index</title>
</head>
<body>
    <h1>Blog Posts</h1>
    <ul>
        {''.join(index_links)}
    </ul>
</body>
</html>"""

index_path = os.path.join(OUTPUT_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(index_html)

print(f"Generated {len(index_links)} posts and index at '{OUTPUT_DIR}'")
