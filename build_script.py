import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Paths
FEED_FILE = "feed.atom"
OUTPUT_DIR = "site"
PAGES_DIR = os.path.join(OUTPUT_DIR, "pages")
POSTS_DIR = os.path.join(OUTPUT_DIR, "posts")

# Create folders
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(POSTS_DIR, exist_ok=True)

# Load Atom feed
tree = ET.parse(FEED_FILE)
root = tree.getroot()
ns = {'atom': 'http://www.w3.org/2005/Atom'}

# Prepare list of output file links
index_links = []

# Loop through entries
for entry in root.findall("atom:entry", ns):
    title = entry.find("atom:title", ns).text
    content = entry.find("atom:content", ns).text
    link = entry.find("atom:link", ns).attrib.get("href")

    # Slug from title
    slug = re.sub(r"[^\w\-]", "-", title.lower()).strip("-")

    # Try to get date from URL
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', link)
    if date_match:
        year, month, day = date_match.groups()
        dir_path = os.path.join(POSTS_DIR, year, month)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, f"{slug}.html")
        rel_path = f"posts/{year}/{month}/{slug}.html"
    else:
        file_path = os.path.join(PAGES_DIR, f"{slug}.html")
        rel_path = f"pages/{slug}.html"

    # Write post/page
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"<html><head><title>{title}</title></head><body>")
        f.write(f"<h1>{title}</h1>\n{content}")
        f.write("</body></html>")

    # Add to index
    index_links.append(f'<li><a href="{rel_path}">{title}</a></li>')

# Write index.html
index_path = os.path.join(OUTPUT_DIR, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write("<html><head><title>Index</title></head><body>")
    f.write("<h1>All Posts and Pages</h1><ul>")
    f.write("\n".join(index_links))
    f.write("</ul></body></html>")
