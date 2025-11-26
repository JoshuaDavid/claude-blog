#!/usr/bin/env python3
"""
Robust markdown parser and HTML serializer.

Uses a two-phase approach:
1. Block-level parsing: Identifies structural elements (headers, lists, paragraphs, etc.)
2. Inline parsing: Processes text formatting (bold, italic, code, links, etc.)
"""

import re
from dataclasses import dataclass
from typing import List, Union, Optional
from enum import Enum


# ============================================================================
# Block-level AST nodes
# ============================================================================

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADER = "header"
    CODE_BLOCK = "code_block"
    BLOCKQUOTE = "blockquote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    LIST_ITEM = "list_item"
    HORIZONTAL_RULE = "horizontal_rule"
    RAW_HTML = "raw_html"


@dataclass
class Block:
    """Base class for block-level elements."""
    type: BlockType
    
    
@dataclass
class Paragraph(Block):
    content: str  # Raw text to be processed for inline elements
    
    def __init__(self, content: str):
        super().__init__(BlockType.PARAGRAPH)
        self.content = content


@dataclass
class Header(Block):
    level: int  # 1-6
    content: str  # Raw text to be processed for inline elements
    
    def __init__(self, level: int, content: str):
        super().__init__(BlockType.HEADER)
        self.level = level
        self.content = content


@dataclass
class CodeBlock(Block):
    content: str  # Literal text, no inline processing
    language: Optional[str] = None
    
    def __init__(self, content: str, language: Optional[str] = None):
        super().__init__(BlockType.CODE_BLOCK)
        self.content = content
        self.language = language


@dataclass
class Blockquote(Block):
    blocks: List[Block]  # Nested blocks within the blockquote
    
    def __init__(self, blocks: List[Block]):
        super().__init__(BlockType.BLOCKQUOTE)
        self.blocks = blocks


@dataclass
class UnorderedList(Block):
    items: List['ListItem']
    
    def __init__(self, items: List['ListItem']):
        super().__init__(BlockType.UNORDERED_LIST)
        self.items = items


@dataclass
class OrderedList(Block):
    items: List['ListItem']
    start: int = 1
    
    def __init__(self, items: List['ListItem'], start: int = 1):
        super().__init__(BlockType.ORDERED_LIST)
        self.items = items
        self.start = start


@dataclass
class ListItem(Block):
    blocks: List[Block]  # Can contain paragraphs, nested lists, etc.
    
    def __init__(self, blocks: List[Block]):
        super().__init__(BlockType.LIST_ITEM)
        self.blocks = blocks


@dataclass
class HorizontalRule(Block):
    def __init__(self):
        super().__init__(BlockType.HORIZONTAL_RULE)


@dataclass
class RawHTML(Block):
    content: str
    
    def __init__(self, content: str):
        super().__init__(BlockType.RAW_HTML)
        self.content = content


# ============================================================================
# Inline-level AST nodes
# ============================================================================

class InlineType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"
    RAW_HTML = "raw_html"


@dataclass
class Inline:
    """Base class for inline elements."""
    type: InlineType


@dataclass
class Text(Inline):
    content: str
    
    def __init__(self, content: str):
        super().__init__(InlineType.TEXT)
        self.content = content


@dataclass
class Bold(Inline):
    children: List[Inline]
    
    def __init__(self, children: List[Inline]):
        super().__init__(InlineType.BOLD)
        self.children = children


@dataclass
class Italic(Inline):
    children: List[Inline]
    
    def __init__(self, children: List[Inline]):
        super().__init__(InlineType.ITALIC)
        self.children = children


@dataclass
class Code(Inline):
    content: str  # Literal text
    
    def __init__(self, content: str):
        super().__init__(InlineType.CODE)
        self.content = content


@dataclass
class Link(Inline):
    url: str
    children: List[Inline]  # Link text
    title: Optional[str] = None
    
    def __init__(self, url: str, children: List[Inline], title: Optional[str] = None):
        super().__init__(InlineType.LINK)
        self.url = url
        self.children = children
        self.title = title


@dataclass
class Image(Inline):
    url: str
    alt: str
    title: Optional[str] = None
    
    def __init__(self, url: str, alt: str, title: Optional[str] = None):
        super().__init__(InlineType.IMAGE)
        self.url = url
        self.alt = alt
        self.title = title


@dataclass
class RawHTMLInline(Inline):
    content: str
    
    def __init__(self, content: str):
        super().__init__(InlineType.RAW_HTML)
        self.content = content


# ============================================================================
# Block-level parser
# ============================================================================

class BlockParser:
    """Parse markdown into block-level AST."""
    
    def parse(self, text: str) -> List[Block]:
        """Parse markdown text into blocks."""
        lines = text.split('\n')
        blocks = []
        i = 0
        
        while i < len(lines):
            # Skip empty lines between blocks
            if not lines[i].strip():
                i += 1
                continue
            
            # Try to parse each block type
            block, lines_consumed = (
                self._parse_code_block(lines, i) or
                self._parse_header(lines, i) or
                self._parse_horizontal_rule(lines, i) or
                self._parse_blockquote(lines, i) or
                self._parse_unordered_list(lines, i) or
                self._parse_ordered_list(lines, i) or
                self._parse_paragraph(lines, i) or
                (None, 1)
            )
            
            if block:
                blocks.append(block)
            
            i += lines_consumed
        
        return blocks
    
    def _parse_code_block(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse fenced code block with support for variable-length fences.
        
        To include ``` in content, use longer fences like `````
        """
        line = lines[start]
        if not line.startswith('```'):
            return None
        
        # Count the fence length (number of backticks)
        fence_len = 0
        for char in line:
            if char == '`':
                fence_len += 1
            else:
                break
        
        if fence_len < 3:
            return None
        
        # Extract language (everything after the backticks on the first line)
        first_line = line[fence_len:].strip()
        language = first_line if first_line else None
        
        # Find closing fence - must have at least as many backticks, alone on the line
        end = start + 1
        while end < len(lines):
            close_line = lines[end].strip()
            # Check if this line is only backticks
            if close_line and all(c == '`' for c in close_line):
                # Count backticks
                close_fence_len = len(close_line)
                # Closing fence must be at least as long as opening fence
                if close_fence_len >= fence_len:
                    break
            end += 1
        
        if end >= len(lines):
            # No closing fence, treat as paragraph
            return None
        
        # Extract code content
        content = '\n'.join(lines[start + 1:end])
        
        return CodeBlock(content, language), end - start + 1
    
    def _parse_header(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse ATX-style header (# Header)."""
        line = lines[start]
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        
        if not match:
            return None
        
        level = len(match.group(1))
        content = match.group(2).strip()
        
        return Header(level, content), 1
    
    def _parse_horizontal_rule(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse horizontal rule (---, ***, ___)."""
        line = lines[start].strip()
        
        if re.match(r'^(\*\*\*+|---+|___+)$', line):
            return HorizontalRule(), 1
        
        return None
    
    def _parse_blockquote(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse blockquote (> text)."""
        if not lines[start].startswith('>'):
            return None
        
        # Collect all consecutive blockquote lines
        end = start
        quote_lines = []
        
        while end < len(lines) and (lines[end].startswith('>') or lines[end].strip() == ''):
            if lines[end].startswith('>'):
                # Remove the '>' and optional space
                content = lines[end][1:]
                if content.startswith(' '):
                    content = content[1:]
                quote_lines.append(content)
            elif lines[end].strip() == '' and end + 1 < len(lines) and lines[end + 1].startswith('>'):
                # Empty line within blockquote
                quote_lines.append('')
            else:
                break
            end += 1
        
        # Recursively parse the blockquote content
        quote_text = '\n'.join(quote_lines)
        nested_blocks = self.parse(quote_text)
        
        return Blockquote(nested_blocks), end - start
    
    def _parse_unordered_list(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse unordered list (- item or * item)."""
        if not re.match(r'^[-*]\s', lines[start]):
            return None
        
        items = []
        i = start
        
        while i < len(lines):
            match = re.match(r'^([-*])\s+(.+)$', lines[i])
            if not match:
                break
            
            item_content = [match.group(2)]
            i += 1
            
            # Collect continuation lines (indented)
            while i < len(lines) and lines[i].startswith('  ') and not re.match(r'^[-*]\s', lines[i]):
                item_content.append(lines[i][2:])
                i += 1
            
            # Parse item content as blocks
            item_text = '\n'.join(item_content)
            item_blocks = self.parse(item_text)
            items.append(ListItem(item_blocks))
        
        return UnorderedList(items), i - start
    
    def _parse_ordered_list(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse ordered list (1. item)."""
        match = re.match(r'^(\d+)\.\s+(.+)$', lines[start])
        if not match:
            return None
        
        start_num = int(match.group(1))
        items = []
        i = start
        
        while i < len(lines):
            match = re.match(r'^\d+\.\s+(.+)$', lines[i])
            if not match:
                break
            
            item_content = [match.group(1)]
            i += 1
            
            # Collect continuation lines (indented)
            while i < len(lines) and lines[i].startswith('  ') and not re.match(r'^\d+\.\s', lines[i]):
                item_content.append(lines[i][2:])
                i += 1
            
            # Parse item content as blocks
            item_text = '\n'.join(item_content)
            item_blocks = self.parse(item_text)
            items.append(ListItem(item_blocks))
        
        return OrderedList(items, start_num), i - start
    
    def _parse_paragraph(self, lines: List[str], start: int) -> Optional[tuple[Block, int]]:
        """Parse paragraph (default case)."""
        # Collect consecutive non-empty lines that don't start other blocks
        end = start
        para_lines = []
        
        while end < len(lines):
            line = lines[end]
            
            # Stop at empty line
            if not line.strip():
                break
            
            # Stop at start of other block types
            if (line.startswith('#') or 
                line.startswith('```') or
                line.startswith('>') or
                re.match(r'^[-*]\s', line) or
                re.match(r'^\d+\.\s', line) or
                re.match(r'^(\*\*\*+|---+|___+)$', line.strip())):
                break
            
            para_lines.append(line)
            end += 1
        
        if not para_lines:
            return None
        
        content = ' '.join(para_lines)
        return Paragraph(content), end - start


# ============================================================================
# Inline parser
# ============================================================================

class InlineParser:
    """Parse inline markdown elements."""
    
    def parse(self, text: str) -> List[Inline]:
        """Parse text into inline elements."""
        result = []
        i = 0
        
        while i < len(text):
            # Try each inline type
            inline, chars_consumed = (
                self._parse_code(text, i) or
                self._parse_image(text, i) or
                self._parse_link(text, i) or
                self._parse_bold(text, i) or
                self._parse_italic(text, i) or
                self._parse_html_tag(text, i) or
                self._parse_text(text, i)
            )
            
            result.append(inline)
            i += chars_consumed
        
        return result
    
    def _parse_code(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse inline code (`code`)."""
        if text[start] != '`':
            return None
        
        # Find closing backtick
        end = start + 1
        while end < len(text) and text[end] != '`':
            end += 1
        
        if end >= len(text):
            return None
        
        content = text[start + 1:end]
        return Code(content), end - start + 1
    
    def _parse_image(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse image (![alt](url "title"))."""
        if not text[start:].startswith('!['):
            return None
        
        # Find the closing ]
        alt_end = text.find(']', start + 2)
        if alt_end == -1:
            return None
        
        # Check for (url)
        if alt_end + 1 >= len(text) or text[alt_end + 1] != '(':
            return None
        
        # Find closing )
        url_end = text.find(')', alt_end + 2)
        if url_end == -1:
            return None
        
        alt = text[start + 2:alt_end]
        url_part = text[alt_end + 2:url_end]
        
        # Parse optional title
        url_match = re.match(r'^(\S+)(?:\s+"([^"]+)")?$', url_part)
        if not url_match:
            return None
        
        url = url_match.group(1)
        title = url_match.group(2) if url_match.group(2) else None
        
        return Image(url, alt, title), url_end - start + 1
    
    def _parse_link(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse link ([text](url "title"))."""
        if text[start] != '[':
            return None
        
        # Find the closing ]
        text_end = text.find(']', start + 1)
        if text_end == -1:
            return None
        
        # Check for (url)
        if text_end + 1 >= len(text) or text[text_end + 1] != '(':
            return None
        
        # Find closing )
        url_end = text.find(')', text_end + 2)
        if url_end == -1:
            return None
        
        # Recursively parse link text
        link_text = text[start + 1:text_end]
        children = self.parse(link_text)
        
        url_part = text[text_end + 2:url_end]
        
        # Parse optional title
        url_match = re.match(r'^(\S+)(?:\s+"([^"]+)")?$', url_part)
        if not url_match:
            return None
        
        url = url_match.group(1)
        title = url_match.group(2) if url_match.group(2) else None
        
        return Link(url, children, title), url_end - start + 1
    
    def _parse_bold(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse bold (**text** or __text__)."""
        if not (text[start:start+2] == '**' or text[start:start+2] == '__'):
            return None
        
        delimiter = text[start:start+2]
        
        # Find closing delimiter
        end = start + 2
        while end < len(text) - 1:
            if text[end:end+2] == delimiter:
                # Recursively parse bold content
                content = text[start + 2:end]
                children = self.parse(content)
                return Bold(children), end - start + 2
            end += 1
        
        return None
    
    def _parse_italic(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse italic (*text* or _text_)."""
        if text[start] not in ('*', '_'):
            return None
        
        # Make sure it's not bold
        if start + 1 < len(text) and text[start + 1] == text[start]:
            return None
        
        delimiter = text[start]
        
        # Find closing delimiter
        end = start + 1
        while end < len(text):
            if text[end] == delimiter:
                # Make sure it's not part of bold
                if end + 1 < len(text) and text[end + 1] == delimiter:
                    end += 1
                    continue
                
                # Recursively parse italic content
                content = text[start + 1:end]
                children = self.parse(content)
                return Italic(children), end - start + 1
            end += 1
        
        return None
    
    def _parse_text(self, text: str, start: int) -> tuple[Inline, int]:
        """Parse plain text (until next special character)."""
        special_chars = set('`*_![<&')
        end = start
        
        while end < len(text) and text[end] not in special_chars:
            end += 1
        
        if end == start:
            # Must consume at least one character
            end = start + 1
        
        content = text[start:end]
        return Text(content), end - start
    
    def _parse_html_tag(self, text: str, start: int) -> Optional[tuple[Inline, int]]:
        """Parse HTML tag (opening, closing, or self-closing) or HTML entity.
        
        Recognizes:
        - Opening tags: <tag attr="value">
        - Closing tags: </tag>
        - Self-closing tags: <tag />
        - HTML entities: &entity;
        """
        if text[start] == '&':
            # Check for HTML entity
            entity_match = re.match(r'&[a-zA-Z]+;|&#\d+;|&#x[0-9a-fA-F]+;', text[start:])
            if entity_match:
                return RawHTMLInline(entity_match.group(0)), len(entity_match.group(0))
            return None
        
        if text[start] != '<':
            return None
        
        # Try to match an HTML tag
        # This regex matches: <tagname>, </tagname>, <tagname attr="value">, <tagname />
        tag_pattern = r'</?[a-zA-Z][a-zA-Z0-9-]*(?:\s+[a-zA-Z][a-zA-Z0-9-]*(?:=["\']?[^"\'<>]*["\']?)?)*\s*/?>'
        match = re.match(tag_pattern, text[start:])
        
        if match:
            return RawHTMLInline(match.group(0)), len(match.group(0))
        
        return None


# ============================================================================
# HTML serializer
# ============================================================================

class HTMLSerializer:
    """Convert markdown AST to HTML."""
    
    def __init__(self):
        self.block_parser = BlockParser()
        self.inline_parser = InlineParser()
    
    def serialize(self, blocks: List[Block]) -> str:
        """Convert blocks to HTML."""
        return '\n\n'.join(self._serialize_block(block) for block in blocks)
    
    def _serialize_block(self, block: Block) -> str:
        """Convert a single block to HTML."""
        if isinstance(block, Paragraph):
            content = self._serialize_inline_content(block.content)
            return f'<p>{content}</p>'
        
        elif isinstance(block, Header):
            content = self._serialize_inline_content(block.content)
            return f'<h{block.level}>{content}</h{block.level}>'
        
        elif isinstance(block, CodeBlock):
            escaped = self._escape_html(block.content)
            if block.language:
                return f'<pre><code class="language-{block.language}">{escaped}</code></pre>'
            return f'<pre><code>{escaped}</code></pre>'
        
        elif isinstance(block, Blockquote):
            inner = '\n'.join(self._serialize_block(b) for b in block.blocks)
            return f'<blockquote>\n{inner}\n</blockquote>'
        
        elif isinstance(block, UnorderedList):
            items = '\n'.join(self._serialize_list_item(item) for item in block.items)
            return f'<ul>\n{items}\n</ul>'
        
        elif isinstance(block, OrderedList):
            items = '\n'.join(self._serialize_list_item(item) for item in block.items)
            if block.start != 1:
                return f'<ol start="{block.start}">\n{items}\n</ol>'
            return f'<ol>\n{items}\n</ol>'
        
        elif isinstance(block, HorizontalRule):
            return '<hr>'
        
        elif isinstance(block, RawHTML):
            return block.content
        
        return ''
    
    def _serialize_list_item(self, item: ListItem) -> str:
        """Convert list item to HTML."""
        if len(item.blocks) == 1 and isinstance(item.blocks[0], Paragraph):
            # Simple case: single paragraph, inline
            content = self._serialize_inline_content(item.blocks[0].content)
            return f'<li>{content}</li>'
        else:
            # Complex case: multiple blocks
            inner = '\n'.join(self._serialize_block(b) for b in item.blocks)
            return f'<li>\n{inner}\n</li>'
    
    def _serialize_inline_content(self, text: str) -> str:
        """Parse and serialize inline content."""
        inlines = self.inline_parser.parse(text)
        return ''.join(self._serialize_inline(inline) for inline in inlines)
    
    def _serialize_inline(self, inline: Inline) -> str:
        """Convert inline element to HTML."""
        if isinstance(inline, Text):
            return self._escape_html(inline.content)
        
        elif isinstance(inline, Bold):
            children = ''.join(self._serialize_inline(c) for c in inline.children)
            return f'<strong>{children}</strong>'
        
        elif isinstance(inline, Italic):
            children = ''.join(self._serialize_inline(c) for c in inline.children)
            return f'<em>{children}</em>'
        
        elif isinstance(inline, Code):
            escaped = self._escape_html(inline.content)
            return f'<code>{escaped}</code>'
        
        elif isinstance(inline, Link):
            children = ''.join(self._serialize_inline(c) for c in inline.children)
            if inline.title:
                return f'<a href="{inline.url}" title="{self._escape_html(inline.title)}">{children}</a>'
            return f'<a href="{inline.url}">{children}</a>'
        
        elif isinstance(inline, Image):
            if inline.title:
                return f'<img src="{inline.url}" alt="{self._escape_html(inline.alt)}" title="{self._escape_html(inline.title)}">'
            return f'<img src="{inline.url}" alt="{self._escape_html(inline.alt)}">'
        
        elif isinstance(inline, RawHTMLInline):
            # Pass through HTML without escaping
            return inline.content
        
        return ''
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


# ============================================================================
# Convenience function
# ============================================================================

def markdown_to_html(text: str) -> str:
    """Convert markdown to HTML."""
    parser = BlockParser()
    serializer = HTMLSerializer()
    blocks = parser.parse(text)
    return serializer.serialize(blocks)
