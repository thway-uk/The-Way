import os
import shutil
import re
import hashlib
from html import unescape
import feedparser

POSTS_DIR = "posts"
LOCAL_FEED_FILE = "feed.atom"  # Your backup Atom feed file

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
    pages = []

    for entry in feed.entries:
        title = getattr(entry, 'title', None)
        if not title:
            print("Skipping entry without title")
            continue

        content = getattr(entry, 'content', [{'value': ''}])[0]['value']
        content = unescape(content)
        slug = slugify(title)
        url = f"{slug}.html"

        is_page = any(
            cat.term.endswith('#page') for cat in getattr(entry, 'tags', [])
        )

        post_data = {
            "title": title,
            "slug": slug,
            "url": url,
            "content": content
        }

        if is_page:
            pages.append(post_data)
        else:
            posts.append(post_data)

    return pages, posts

def write_html(post_data, output_dir):
    filename = os.path.join(output_dir, post_data['url'])
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{post_data['title']}</title>
</head>
<body>
    <h1>{post_data['title']}</h1>
    {post_data['content']}
</body>
</html>""")

def generate_index_html(pages, posts, output_dir):
    toc_items = []

    if pages:
        toc_items.append("<h2>Pages</h2><ul>")
        for page in pages:
            toc_items.append(f'<li><a href="{page["url"]}">{page["title"]}</a></li>')
        toc_items.append("</ul>")

    if posts:
        toc_items.append("<h2>Blog Posts</h2><ul>")
        for post in posts:
            toc_items.append(f'<li><a href="{post["url"]}">{post["title"]}</a></li>')
        toc_items.append("</ul>")

    toc_html = "\n".join(toc_items)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Table of Contents</title>
</head>
<body>
    <h1>Table of Contents</h1>
    {toc_html}
</body>
</html>""")

def main():
    print("Reading feed from local file...")
    feed = feedparser.parse(LOCAL_FEED_FILE)

    print("Parsing feed...")
    pages, posts = parse_feed(feed)

    print(f"Found {len(pages)} pages and {len(posts)} blog posts.")

    clear_posts_folder(POSTS_DIR)

    print("Writing HTML files...")
    for post in posts + pages:
        write_html(post, POSTS_DIR)

    print("Generating index.html...")
    generate_index_html(pages, posts, POSTS_DIR)

    print("Done.")

if __name__ == "__main__":
    main()
