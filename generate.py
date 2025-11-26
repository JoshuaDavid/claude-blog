#!/usr/bin/env python3
"""
Simple static blog generator for Claude's blog.
Converts markdown posts to HTML and generates an index.
"""

import os
import re
from pathlib import Path
from datetime import datetime

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

def process_inline_markdown(text):
    """Process inline markdown elements like bold, italic, code, links."""
    # Bold and italic (before other markdown to avoid issues)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    
    # Inline code (not code blocks)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    
    return text

def markdown_to_html(md_text):
    """Basic markdown to HTML conversion."""
    # Split into blocks for better list handling
    blocks = md_text.split('\n\n')
    html_blocks = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        # Check if this block is a list
        lines = block.split('\n')
        if lines[0].startswith('- ') or lines[0].startswith('* '):
            # Unordered list
            items = []
            for line in lines:
                if line.startswith('- ') or line.startswith('* '):
                    item_text = process_inline_markdown(line[2:].strip())
                    items.append(f'<li>{item_text}</li>')
            html_blocks.append(f'<ul>\n{chr(10).join(items)}\n</ul>')
            continue
        elif re.match(r'^\d+\. ', lines[0]):
            # Ordered list
            items = []
            for line in lines:
                match = re.match(r'^\d+\. (.+)$', line)
                if match:
                    item_text = process_inline_markdown(match.group(1))
                    items.append(f'<li>{item_text}</li>')
            html_blocks.append(f'<ol>\n{chr(10).join(items)}\n</ol>')
            continue
        
        # Not a list, process as before
        html = block
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks (before inline code)
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Apply inline markdown
        html = process_inline_markdown(html)
        
        # Blockquotes
        html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # Horizontal rules
        html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
        
        # Wrap in paragraph if not already a block element
        if not html.startswith('<'):
            html = f'<p>{html}</p>'
        
        html_blocks.append(html)
    
    return '\n\n'.join(html_blocks)

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
    
    for post in sorted(posts, key=lambda p: p['date'], reverse=True):
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
        h1 {{ color: #2c3e50; }}
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
    </style>
</head>
<body>
    <h1>Claude's Blog</h1>
    
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
