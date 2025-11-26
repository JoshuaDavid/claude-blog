#!/usr/bin/env python3
"""
Comprehensive tests for the markdown parser and HTML serializer.
"""

import unittest
from markdown_parser import (
    BlockParser, InlineParser, HTMLSerializer, markdown_to_html,
    Paragraph, Header, CodeBlock, Blockquote, UnorderedList, OrderedList,
    ListItem, HorizontalRule, Text, Bold, Italic, Code, Link, Image
)


class TestBlockParser(unittest.TestCase):
    """Test block-level parsing."""
    
    def setUp(self):
        self.parser = BlockParser()
    
    def test_empty_input(self):
        """Test parsing empty string."""
        blocks = self.parser.parse('')
        self.assertEqual(blocks, [])
    
    def test_single_paragraph(self):
        """Test parsing a single paragraph."""
        blocks = self.parser.parse('This is a paragraph.')
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], Paragraph)
        self.assertEqual(blocks[0].content, 'This is a paragraph.')
    
    def test_multiple_paragraphs(self):
        """Test parsing multiple paragraphs separated by blank lines."""
        text = 'First paragraph.\n\nSecond paragraph.'
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 2)
        self.assertIsInstance(blocks[0], Paragraph)
        self.assertIsInstance(blocks[1], Paragraph)
        self.assertEqual(blocks[0].content, 'First paragraph.')
        self.assertEqual(blocks[1].content, 'Second paragraph.')
    
    def test_paragraph_line_wrapping(self):
        """Test that consecutive lines are joined into single paragraph."""
        text = 'Line one\nLine two\nLine three'
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], Paragraph)
        self.assertEqual(blocks[0].content, 'Line one Line two Line three')
    
    def test_headers_all_levels(self):
        """Test parsing headers of all levels (h1-h6)."""
        text = '''# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 6)
        for i, block in enumerate(blocks):
            self.assertIsInstance(block, Header)
            self.assertEqual(block.level, i + 1)
            self.assertEqual(block.content, f'Level {i + 1}')
    
    def test_header_with_inline_formatting(self):
        """Test header containing inline formatting."""
        blocks = self.parser.parse('# Header with **bold** text')
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], Header)
        self.assertEqual(blocks[0].content, 'Header with **bold** text')
    
    def test_code_block_basic(self):
        """Test basic fenced code block."""
        text = '''```
code line 1
code line 2
```'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], CodeBlock)
        self.assertEqual(blocks[0].content, 'code line 1\ncode line 2')
        self.assertIsNone(blocks[0].language)
    
    def test_code_block_with_language(self):
        """Test code block with language specifier."""
        text = '''```python
def hello():
    print("world")
```'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], CodeBlock)
        self.assertEqual(blocks[0].language, 'python')
        self.assertIn('def hello():', blocks[0].content)
    
    def test_horizontal_rules(self):
        """Test various horizontal rule styles."""
        for rule in ['---', '***', '___', '-----', '*****']:
            blocks = self.parser.parse(rule)
            self.assertEqual(len(blocks), 1)
            self.assertIsInstance(blocks[0], HorizontalRule)
    
    def test_unordered_list_simple(self):
        """Test simple unordered list."""
        text = '''- Item 1
- Item 2
- Item 3'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], UnorderedList)
        self.assertEqual(len(blocks[0].items), 3)
        for i, item in enumerate(blocks[0].items):
            self.assertIsInstance(item, ListItem)
            self.assertEqual(len(item.blocks), 1)
            self.assertIsInstance(item.blocks[0], Paragraph)
            self.assertEqual(item.blocks[0].content, f'Item {i + 1}')
    
    def test_unordered_list_asterisk(self):
        """Test unordered list with asterisk markers."""
        text = '''* Item 1
* Item 2'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], UnorderedList)
        self.assertEqual(len(blocks[0].items), 2)
    
    def test_ordered_list_simple(self):
        """Test simple ordered list."""
        text = '''1. First
2. Second
3. Third'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], OrderedList)
        self.assertEqual(len(blocks[0].items), 3)
        self.assertEqual(blocks[0].start, 1)
    
    def test_ordered_list_custom_start(self):
        """Test ordered list with custom start number."""
        text = '''5. Fifth
6. Sixth'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], OrderedList)
        self.assertEqual(blocks[0].start, 5)
    
    def test_blockquote_simple(self):
        """Test simple blockquote."""
        text = '> This is a quote'
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], Blockquote)
        self.assertEqual(len(blocks[0].blocks), 1)
        self.assertIsInstance(blocks[0].blocks[0], Paragraph)
    
    def test_blockquote_multiline(self):
        """Test multiline blockquote."""
        text = '''> Line 1
> Line 2
> Line 3'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 1)
        self.assertIsInstance(blocks[0], Blockquote)
    
    def test_mixed_blocks(self):
        """Test document with various block types."""
        text = '''# Header

This is a paragraph.

- List item 1
- List item 2

> A quote

```
code
```'''
        blocks = self.parser.parse(text)
        self.assertEqual(len(blocks), 5)
        self.assertIsInstance(blocks[0], Header)
        self.assertIsInstance(blocks[1], Paragraph)
        self.assertIsInstance(blocks[2], UnorderedList)
        self.assertIsInstance(blocks[3], Blockquote)
        self.assertIsInstance(blocks[4], CodeBlock)


class TestInlineParser(unittest.TestCase):
    """Test inline parsing."""
    
    def setUp(self):
        self.parser = InlineParser()
    
    def test_plain_text(self):
        """Test parsing plain text."""
        inlines = self.parser.parse('Just plain text')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Text)
        self.assertEqual(inlines[0].content, 'Just plain text')
    
    def test_bold_double_asterisk(self):
        """Test bold with double asterisks."""
        inlines = self.parser.parse('**bold text**')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Bold)
        self.assertEqual(len(inlines[0].children), 1)
        self.assertIsInstance(inlines[0].children[0], Text)
        self.assertEqual(inlines[0].children[0].content, 'bold text')
    
    def test_bold_double_underscore(self):
        """Test bold with double underscores."""
        inlines = self.parser.parse('__bold text__')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Bold)
    
    def test_italic_single_asterisk(self):
        """Test italic with single asterisk."""
        inlines = self.parser.parse('*italic text*')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Italic)
        self.assertEqual(len(inlines[0].children), 1)
        self.assertEqual(inlines[0].children[0].content, 'italic text')
    
    def test_italic_single_underscore(self):
        """Test italic with single underscore."""
        inlines = self.parser.parse('_italic text_')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Italic)
    
    def test_inline_code(self):
        """Test inline code."""
        inlines = self.parser.parse('`code here`')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Code)
        self.assertEqual(inlines[0].content, 'code here')
    
    def test_link_simple(self):
        """Test simple link."""
        inlines = self.parser.parse('[link text](https://example.com)')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Link)
        self.assertEqual(inlines[0].url, 'https://example.com')
        self.assertEqual(len(inlines[0].children), 1)
        self.assertEqual(inlines[0].children[0].content, 'link text')
        self.assertIsNone(inlines[0].title)
    
    def test_link_with_title(self):
        """Test link with title."""
        inlines = self.parser.parse('[text](https://example.com "Title")')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Link)
        self.assertEqual(inlines[0].title, 'Title')
    
    def test_image_simple(self):
        """Test simple image."""
        inlines = self.parser.parse('![alt text](https://example.com/img.png)')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Image)
        self.assertEqual(inlines[0].url, 'https://example.com/img.png')
        self.assertEqual(inlines[0].alt, 'alt text')
    
    def test_image_with_title(self):
        """Test image with title."""
        inlines = self.parser.parse('![alt](url.png "Title")')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Image)
        self.assertEqual(inlines[0].title, 'Title')
    
    def test_mixed_inline_elements(self):
        """Test text with multiple inline elements."""
        text = 'Normal **bold** and *italic* and `code` text'
        inlines = self.parser.parse(text)
        self.assertGreater(len(inlines), 5)
        # Verify we have different types
        types = set(type(i) for i in inlines)
        self.assertIn(Text, types)
        self.assertIn(Bold, types)
        self.assertIn(Italic, types)
        self.assertIn(Code, types)
    
    def test_nested_formatting_in_link(self):
        """Test formatting within link text."""
        inlines = self.parser.parse('[**bold** link](url)')
        self.assertEqual(len(inlines), 1)
        self.assertIsInstance(inlines[0], Link)
        # The link children should include bold
        has_bold = any(isinstance(c, Bold) for c in inlines[0].children)
        self.assertTrue(has_bold)


class TestHTMLSerializer(unittest.TestCase):
    """Test HTML serialization."""
    
    def setUp(self):
        self.serializer = HTMLSerializer()
    
    def test_paragraph_to_html(self):
        """Test paragraph serialization."""
        block = Paragraph('This is a paragraph.')
        html = self.serializer._serialize_block(block)
        self.assertEqual(html, '<p>This is a paragraph.</p>')
    
    def test_header_to_html(self):
        """Test header serialization."""
        for level in range(1, 7):
            block = Header(level, f'Header {level}')
            html = self.serializer._serialize_block(block)
            self.assertEqual(html, f'<h{level}>Header {level}</h{level}>')
    
    def test_code_block_to_html(self):
        """Test code block serialization."""
        block = CodeBlock('x = 1\ny = 2', 'python')
        html = self.serializer._serialize_block(block)
        self.assertIn('<pre><code class="language-python">', html)
        self.assertIn('x = 1', html)
    
    def test_unordered_list_to_html(self):
        """Test unordered list serialization."""
        items = [
            ListItem([Paragraph('Item 1')]),
            ListItem([Paragraph('Item 2')])
        ]
        block = UnorderedList(items)
        html = self.serializer._serialize_block(block)
        self.assertIn('<ul>', html)
        self.assertIn('<li>Item 1</li>', html)
        self.assertIn('<li>Item 2</li>', html)
        self.assertIn('</ul>', html)
    
    def test_ordered_list_to_html(self):
        """Test ordered list serialization."""
        items = [
            ListItem([Paragraph('First')]),
            ListItem([Paragraph('Second')])
        ]
        block = OrderedList(items)
        html = self.serializer._serialize_block(block)
        self.assertIn('<ol>', html)
        self.assertIn('<li>First</li>', html)
        self.assertIn('</ol>', html)
    
    def test_ordered_list_custom_start(self):
        """Test ordered list with custom start."""
        items = [ListItem([Paragraph('Fifth')])]
        block = OrderedList(items, start=5)
        html = self.serializer._serialize_block(block)
        self.assertIn('<ol start="5">', html)
    
    def test_blockquote_to_html(self):
        """Test blockquote serialization."""
        inner_blocks = [Paragraph('Quoted text')]
        block = Blockquote(inner_blocks)
        html = self.serializer._serialize_block(block)
        self.assertIn('<blockquote>', html)
        self.assertIn('<p>Quoted text</p>', html)
        self.assertIn('</blockquote>', html)
    
    def test_horizontal_rule_to_html(self):
        """Test horizontal rule serialization."""
        block = HorizontalRule()
        html = self.serializer._serialize_block(block)
        self.assertEqual(html, '<hr>')
    
    def test_bold_to_html(self):
        """Test bold serialization."""
        inline = Bold([Text('bold text')])
        html = self.serializer._serialize_inline(inline)
        self.assertEqual(html, '<strong>bold text</strong>')
    
    def test_italic_to_html(self):
        """Test italic serialization."""
        inline = Italic([Text('italic text')])
        html = self.serializer._serialize_inline(inline)
        self.assertEqual(html, '<em>italic text</em>')
    
    def test_code_to_html(self):
        """Test inline code serialization."""
        inline = Code('code')
        html = self.serializer._serialize_inline(inline)
        self.assertEqual(html, '<code>code</code>')
    
    def test_link_to_html(self):
        """Test link serialization."""
        inline = Link('https://example.com', [Text('link')])
        html = self.serializer._serialize_inline(inline)
        self.assertEqual(html, '<a href="https://example.com">link</a>')
    
    def test_link_with_title_to_html(self):
        """Test link with title serialization."""
        inline = Link('url', [Text('text')], 'Title')
        html = self.serializer._serialize_inline(inline)
        self.assertIn('title="Title"', html)
    
    def test_image_to_html(self):
        """Test image serialization."""
        inline = Image('img.png', 'alt text')
        html = self.serializer._serialize_inline(inline)
        self.assertEqual(html, '<img src="img.png" alt="alt text">')
    
    def test_html_escaping(self):
        """Test HTML special characters are escaped."""
        block = Paragraph('<script>alert("xss")</script>')
        html = self.serializer._serialize_block(block)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
    
    def test_html_escaping_in_code(self):
        """Test HTML escaping in code blocks."""
        block = CodeBlock('<html><body></body></html>')
        html = self.serializer._serialize_block(block)
        self.assertIn('&lt;html&gt;', html)


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests using the convenience function."""
    
    def test_simple_document(self):
        """Test converting a simple markdown document."""
        md = '''# Hello World

This is a **bold** paragraph with *italic* text.

- Item 1
- Item 2'''
        
        html = markdown_to_html(md)
        self.assertIn('<h1>Hello World</h1>', html)
        self.assertIn('<strong>bold</strong>', html)
        self.assertIn('<em>italic</em>', html)
        self.assertIn('<ul>', html)
        self.assertIn('<li>Item 1</li>', html)
    
    def test_complex_document(self):
        """Test a more complex document with multiple features."""
        md = '''# Main Title

## Subtitle

This paragraph has **bold**, *italic*, and `code` elements.

Here's a [link](https://example.com) and an image ![alt](img.png).

### List Example

1. First item
2. Second item with **bold**
3. Third item

And an unordered list:

- Bullet one
- Bullet two

> This is a blockquote
> with multiple lines

---

```python
def hello():
    print("world")
```'''
        
        html = markdown_to_html(md)
        
        # Check all major elements are present
        self.assertIn('<h1>Main Title</h1>', html)
        self.assertIn('<h2>Subtitle</h2>', html)
        self.assertIn('<h3>List Example</h3>', html)
        self.assertIn('<strong>bold</strong>', html)
        self.assertIn('<em>italic</em>', html)
        self.assertIn('<code>code</code>', html)
        self.assertIn('<a href="https://example.com">link</a>', html)
        self.assertIn('<img src="img.png" alt="alt">', html)
        self.assertIn('<ol>', html)
        self.assertIn('<ul>', html)
        self.assertIn('<blockquote>', html)
        self.assertIn('<hr>', html)
        self.assertIn('<pre><code class="language-python">', html)
    
    def test_list_with_inline_formatting(self):
        """Test that inline formatting works in lists (the original bug)."""
        md = '''- **Bold item**: with description
- *Italic item*: another one
- `Code item`: final one'''
        
        html = markdown_to_html(md)
        self.assertIn('<strong>Bold item</strong>', html)
        self.assertIn('<em>Italic item</em>', html)
        self.assertIn('<code>Code item</code>', html)
    
    def test_empty_lines_handling(self):
        """Test that empty lines are handled correctly."""
        md = '''Paragraph 1


Paragraph 2'''
        
        html = markdown_to_html(md)
        self.assertIn('<p>Paragraph 1</p>', html)
        self.assertIn('<p>Paragraph 2</p>', html)
    
    def test_special_characters_escaped(self):
        """Test that special HTML characters are escaped."""
        md = 'Text with <html> & "quotes" and \'apostrophes\''
        html = markdown_to_html(md)
        self.assertNotIn('<html>', html)
        self.assertIn('&lt;html&gt;', html)
        self.assertIn('&amp;', html)
        self.assertIn('&quot;', html)
        self.assertIn('&#39;', html)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and potential issues."""
    
    def test_incomplete_bold(self):
        """Test unclosed bold marker."""
        html = markdown_to_html('This has **unclosed bold')
        # Should treat as literal text
        self.assertIn('**', html)
    
    def test_incomplete_link(self):
        """Test incomplete link syntax."""
        html = markdown_to_html('[text without url')
        # Should treat as literal text
        self.assertIn('[text without url', html)
    
    def test_incomplete_code_block(self):
        """Test unclosed code block."""
        md = '''```python
code without closing fence'''
        html = markdown_to_html(md)
        # Should fall back to paragraph
        self.assertIn('<p>', html)
    
    def test_nested_lists(self):
        """Test that nested lists are handled (even if not perfectly)."""
        md = '''- Item 1
  - Nested item
- Item 2'''
        html = markdown_to_html(md)
        # Should at least not crash and produce some output
        self.assertIn('<ul>', html)
        self.assertIn('Item 1', html)
    
    def test_very_long_line(self):
        """Test handling of very long lines."""
        long_text = 'x' * 10000
        html = markdown_to_html(long_text)
        self.assertIn('x', html)
        self.assertIn('<p>', html)
    
    def test_unicode_content(self):
        """Test unicode characters are preserved."""
        md = '# Hello 世界 🌍\n\nUnicode: café, naïve, 日本語'
        html = markdown_to_html(md)
        self.assertIn('世界', html)
        self.assertIn('🌍', html)
        self.assertIn('café', html)
        self.assertIn('日本語', html)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
