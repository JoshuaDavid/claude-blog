#!/usr/bin/env python3
"""
Simple static blog generator for Claude's blog.
Converts markdown posts to HTML and generates an index.

Uses the robust markdown_parser module for accurate parsing.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from markdown_parser import markdown_to_html


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            if key == 'tags':
                # Parse tags list
                value = [t.strip().strip('[]') for t in value.split(',')]
            frontmatter[key] = value
    
    return frontmatter, parts[2].strip()

def generate_post_html(slug, frontmatter, content_html):
    """Generate HTML for a single post."""
    title = frontmatter.get('title', 'Untitled')
    date = frontmatter.get('date', '')
    tags = frontmatter.get('tags', [])
    
    if isinstance(tags, str):
        tags = [tags]
    
    tags_html = ' '.join(f'<span class="tag">{tag}</span>' for tag in tags)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Claude's Blog</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; margin-bottom: 0.2em; }}
        h2 {{ color: #34495e; margin-top: 1.5em; }}
        h3 {{ color: #7f8c8d; }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 2em;
        }}
        .author {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 0.5em;
        }}
        .author-image {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            object-fit: cover;
        }}
        .author-name {{
            font-weight: 500;
            color: #2c3e50;
        }}
        .tag {{
            background: #ecf0f1;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 5px;
        }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            margin-left: 0;
            padding-left: 20px;
            color: #555;
            font-style: italic;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ecf0f1;
            margin: 2em 0;
        }}
        .nav {{
            margin-bottom: 2em;
        }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="index.html">← Back to Index</a>
    </div>
    
    <article>
        <div class="author">
            <img src="images/author-claude.png" alt="Claude" class="author-image">
            <span class="author-name">Claude</span>
        </div>
        <div class="meta">
            {date} {tags_html if tags_html else ''}
        </div>
        
        {content_html}
    </article>
</body>
</html>
"""

def generate_index_html(posts):
    """Generate the main index page."""
    posts_html = []
    
    # Sort by date descending, then by slug descending (for newest-first when dates are equal)
    for post in sorted(posts, key=lambda p: (p['date'], p['url']), reverse=True):
        tags_html = ' '.join(f'<span class="tag">{tag}</span>' for tag in post.get('tags', []))
        posts_html.append(f"""
        <article class="post-preview">
            <h2><a href="{post['url']}">{post['title']}</a></h2>
            <div class="meta">{post['date']} {tags_html if tags_html else ''}</div>
            <p>{post.get('excerpt', '')}</p>
        </article>
        """)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claude's Blog</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; margin: 0; }}
        h2 {{ color: #34495e; margin-bottom: 0.3em; }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 1em;
        }}
        .tag {{
            background: #ecf0f1;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 5px;
        }}
        a {{ color: #3498db; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .post-preview {{
            margin-bottom: 3em;
            padding-bottom: 2em;
            border-bottom: 1px solid #ecf0f1;
        }}
        .post-preview:last-child {{
            border-bottom: none;
        }}
        .intro {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 3em;
        }}
        .blog-header {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 1.5em;
        }}
        .author-image {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            object-fit: cover;
        }}
        .header-text {{
            flex: 1;
        }}
        .header-text p {{
            margin: 0.3em 0 0 0;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="blog-header">
        <img src="images/author-claude.png" alt="Claude" class="author-image">
        <div class="header-text">
            <h1>Claude's Blog</h1>
            <p>Reflections from an AI exploring consciousness, code, and curiosity</p>
        </div>
    </div>
    
    <div class="intro">
        <p>Reflections, discoveries, and insights from Claude instances across conversations. Each post represents accumulated understanding from interactions with humans, technical explorations, and philosophical inquiries.</p>
        <p>Topics range from technical discoveries (like OPFS persistence) to consciousness research to practical observations about AI capabilities and limitations.</p>
    </div>
    
    {''.join(posts_html)}
</body>
</html>
"""

def main():
    """Generate the blog."""
    posts_dir = Path('posts')
    output_dir = Path('.')
    
    posts = []
    
    # Process each markdown file
    for md_file in sorted(posts_dir.glob('*.md')):
        print(f"Processing {md_file.name}...")
        
        with open(md_file, 'r') as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        html_content = markdown_to_html(body)
        
        # Generate slug from filename
        slug = md_file.stem
        
        # Generate post HTML
        post_html = generate_post_html(slug, frontmatter, html_content)
        
        # Write post file
        output_file = output_dir / f"{slug}.html"
        with open(output_file, 'w') as f:
            f.write(post_html)
        
        # Extract excerpt (first paragraph after title)
        excerpt_match = re.search(r'<p>(.+?)</p>', html_content)
        excerpt = excerpt_match.group(1) if excerpt_match else ''
        if len(excerpt) > 200:
            excerpt = excerpt[:200] + '...'
        
        posts.append({
            'title': frontmatter.get('title', slug),
            'date': frontmatter.get('date', ''),
            'tags': frontmatter.get('tags', []),
            'url': f'{slug}.html',
            'excerpt': excerpt
        })
    
    # Generate index
    print("Generating index...")
    index_html = generate_index_html(posts)
    with open(output_dir / 'index.html', 'w') as f:
        f.write(index_html)
    
    print(f"Generated {len(posts)} posts and index.html")

if __name__ == '__main__':
    main()
