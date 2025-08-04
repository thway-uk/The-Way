import os
import shutil
import re
from html import unescape
import feedparser
from datetime import datetime

POSTS_DIR = "posts"
LOCAL_FEED_FILE = "feed.atom"

def slugify(text):
    text = text.lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-]', '', text)
    return text.strip('-')

def clear_posts_folder(posts_dir):
    if os.path.exists(posts_dir):
        print(f"Clearing existing posts folder: {posts_dir}")
        shutil.rmtree(posts_dir)
    os.makedirs(posts_dir, exist_ok=True)

def parse_feed(feed):
    pages = []
    posts = []

    for entry in feed.entries:
        title = getattr(entry, 'title', None)
        if not title:
            continue

        tags = getattr(entry, 'tags', [])
        # Precise detection of pages by exact match
        is_page = any(tag.term == "http://schemas.google.com/blogger/2008/kind#page" for tag in tags)

        content = getattr(entry, 'content', [{'value': ''}])[0]['value']
        content = unescape(content)
        slug = slugify(title)

        # Use published date for folder structure
        if hasattr(entry, 'published_parsed'):
            dt = datetime(*entry.published_parsed[:6])
            date_path = f"{dt.year}/{dt.month:02d}"
        else:
            date_path = "undated"

        post_data = {
            "title": title,
            "slug": slug,
            "content": content,
            "date_path": date_path,
            "is_page": is_page
        }

        if is_page:
            pages.append(post_data)
        else:
            posts.append(post_data)

    return pages, posts

def write_post_html(post_data):
    folder_path = os.path.join(POSTS_DIR, post_data['date_path'])
    os.makedirs(folder_path, exist_ok=True)

    filepath = os.path.join(folder_path, f"{post_data['slug']}.html")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{post_data['title']}</title></head>
<body>
<h1>{post_data['title']}</h1>
{post_data['content']}
</body>
</html>""")

def generate_index_html(pages, posts):
    toc_html = "<h2>Pages</h2><ul>"
    for page in pages:
        href = f"{page['date_path']}/{page['slug']}.html"
        toc_html += f'<li><a href="{href}">{page["title"]}</a></li>'
    toc_html += "</ul>"

    toc_html += "<h2>Posts</h2><ul>"
    for post in posts:
        href = f"{post['date_path']}/{post['slug']}.html"
        toc_html += f'<li><a href="{href}">{post["title"]}</a></li>'
    toc_html += "</ul>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Table of Contents</title></head>
<body>
<h1>Table of Contents</h1>
{toc_html}
</body>
</html>""")

def main():
    feed = feedparser.parse(LOCAL_FEED_FILE)
    pages, posts = parse_feed(feed)

    clear_posts_folder(POSTS_DIR)

    for item in pages + posts:
        write_post_html(item)

    generate_index_html(pages, posts)
    print(f"Done: {len(posts)} posts and {len(pages)} pages generated.")

if __name__ == "__main__":
    main()
