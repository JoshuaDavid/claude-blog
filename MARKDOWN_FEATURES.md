# Markdown Parser Features

This markdown parser implements a robust two-phase parsing system with support for all common markdown features.

## Supported Elements

### Block-Level Elements
- **Headers**: `# H1` through `###### H6`
- **Paragraphs**: Consecutive lines are joined into paragraphs
- **Code Blocks**: Fenced with ``` (with optional language)
- **Blockquotes**: Lines starting with `>`
- **Unordered Lists**: Lines starting with `-` or `*`
- **Ordered Lists**: Lines starting with `1.`, `2.`, etc.
- **Horizontal Rules**: `---`, `***`, or `___`

### Inline Elements
- **Bold**: `**text**` or `__text__`
- **Italic**: `*text*` or `_text_`
- **Inline Code**: `` `code` ``
- **Links**: `[text](url)` or `[text](url "title")`
- **Images**: `![alt](url)` or `![alt](url "title")`

## Advanced Features

### Variable-Length Code Fences

To include ``` as content in a code block, use longer fences:

````markdown
`````
This code block can contain:
```
shorter fences
```
as literal content!
`````
````

The parser counts backticks in the opening fence and requires at least that many in the closing fence. This follows GitHub-Flavored Markdown conventions.

### Inline Formatting in Lists

Lists fully support inline formatting:

```markdown
- **Bold item**: with description
- *Italic item*: another one  
- `Code item`: with code
- [Link item](url): with links
```

### HTML Escaping

All HTML special characters are properly escaped:
- `<` becomes `&lt;`
- `>` becomes `&gt;`
- `&` becomes `&amp;`
- `"` becomes `&quot;`
- `'` becomes `&#39;`

This prevents XSS attacks and ensures code examples display correctly.

### Nested Inline Elements

The parser supports nested inline formatting:
- `**bold with *italic* inside**`
- `[**bold link**](url)`
- `*italic with `code` inside*` (note: this is tricky and has limits)

## Parser Architecture

### Two-Phase Design

1. **Block Parser**: Identifies document structure (headers, lists, paragraphs, etc.)
2. **Inline Parser**: Processes text formatting within blocks (bold, links, etc.)

This separation makes the parser more robust than regex-only approaches and easier to extend than monolithic parsers.

### AST Representation

The parser builds an Abstract Syntax Tree (AST) before generating HTML:

```
Document
├── Header (level=1)
│   └── Text("Hello")
├── Paragraph
│   ├── Text("This is ")
│   └── Bold
│       └── Text("bold")
└── UnorderedList
    ├── ListItem
    │   └── Paragraph
    │       └── Text("Item 1")
    └── ListItem
        └── Paragraph
            └── Text("Item 2")
```

This makes the output predictable and the parser extensible.

## Testing

The parser has 61+ comprehensive tests covering:
- All block and inline elements
- Edge cases (unclosed markers, empty input, very long lines)
- Unicode handling
- HTML escaping
- Nested structures
- Variable-length fences

Run tests with:
```bash
python3 test_markdown_parser.py
```

## Known Limitations

1. **No nested lists**: Indented list items are treated as continuations, not nested lists
2. **No tables**: GitHub-style tables are not supported
3. **No task lists**: `- [ ]` checkbox syntax is not supported
4. **No strikethrough**: `~~text~~` is not supported
5. **No superscript/subscript**: LaTeX-style or HTML-style super/subscripts not supported

These limitations are by design to keep the parser simple and maintainable. They can be added if needed.

## Usage

```python
from markdown_parser import markdown_to_html

markdown = """
# Hello World

This is **bold** and *italic* text.

- Item 1
- Item 2
"""

html = markdown_to_html(markdown)
print(html)
```

For blog generation, see `generate.py` which uses this parser with frontmatter support.
