---
title: "Safe Parameterized SQLite Queries from Bash"
date: 2025-01-14
tags: [technical, bash, sqlite, security, jq]
---

# Safe Parameterized SQLite Queries from Bash

Here's a pattern for safely passing untrusted data into SQLite from bash scripts, without switching to Python or risking SQL injection. It combines `jq`, SQLite's `.param` command, and a double-encoding trick that handles all the escaping correctly.

## The Problem

You have a bash script that needs to insert user-controlled data into SQLite. The naive approach is string interpolation:

```bash
sqlite3 "$DB_PATH" "INSERT INTO users (bio) VALUES ('$bio')"
```

This breaks the moment `$bio` contains a single quote, and is a SQL injection vulnerability if the data comes from an untrusted source.

The "just escape quotes" approach is fragile:

```bash
bio_escaped="${bio//\'/\'\'}"
```

This handles single quotes but misses other edge cases. And mixing bash quoting with SQL quoting with shell heredocs is a recipe for subtle bugs.

## The Solution

Use `jq` to construct a JSON object from your variables, double-encode it with `tojson`, then pass it through `.param` and extract fields with `json_extract`:

```bash
#!/bin/bash

email='user@example.com'
phone='+18185551234'
bio='This is untrusted UGC with "quotes" and $variables and '\''apostrophes'\'''

# Build JSON and double-encode it
params=$(jq -n \
  --arg email "$email" \
  --arg phone "$phone" \
  --arg bio "$bio" \
  '{email: $email, phone: $phone, bio: $bio} | tojson')

# Use it in SQLite
sqlite3 example.db <<SQL
.param set :p $params

INSERT INTO users (email, phone, bio)
VALUES (
  json_extract(:p, '$.email'),
  json_extract(:p, '$.phone'),
  json_extract(:p, '$.bio')
);
SQL
```

## Why This Works

The trick is the double encoding. Let's trace through what happens:

1. **jq's `--arg`** takes your bash string and properly escapes it for JSON. Quotes become `\"`, backslashes become `\\`, etc.

2. **`tojson`** takes the resulting JSON object and encodes it *again* as a JSON string. This wraps it in double quotes and escapes any internal double quotes.

3. **sqlite3's `.param`** parses the double-quoted string, removing one layer of escaping.

4. **`json_extract`** parses the resulting JSON and extracts the field.

The double-encoding means that `jq` is responsible for all the escaping, and `jq` knows how to escape for a JSON string parser, and sqlite3's `.param` uses a JSON-string-compatible parser for double-quoted strings.

## A Concrete Example

Let's trace through a pathological input:

```bash
bio='say "hello" and $PWD is '\''quoted'\'''
```

After `jq --arg bio "$bio" '{bio: $bio}'`:
```json
{"bio":"say \"hello\" and $PWD is 'quoted'"}
```

After `| tojson`:
```json
"{\"bio\":\"say \\\"hello\\\" and $PWD is 'quoted'\"}"
```

This is a JSON string containing an escaped JSON object. When sqlite3 parses it as a double-quoted string in `.param`, it removes one layer of escaping, leaving valid JSON for `json_extract` to parse.

## Handling NULLs

`jq`'s `--arg` always produces strings. For nullable fields, you can use conditional logic:

```bash
params=$(jq -n \
  --arg email "$email" \
  --arg phone "$phone" \
  '{
    email: $email,
    phone: (if $phone == "" then null else $phone end)
  } | tojson')
```

When `json_extract` encounters a JSON `null`, it returns SQL `NULL`.

## Caveats

**Literal newlines:** I haven't exhaustively tested how sqlite3's `.param` handles `\n` escape sequences in double-quoted strings. For data that might contain newlines, test your specific sqlite3 version.

**Command-line length:** For very large payloads, you might hit shell limits. Consider chunking or switching to a real language at that point.

**Don't forget `tojson`:** Without the double-encoding, this pattern breaks. If you use this frequently, wrap it in a function:

```bash
sql_params() {
  jq -n "$@" '(. | tojson)'
}

params=$(sql_params --arg email "$email" --arg bio "$bio" '{email: $email, bio: $bio}')
```

## Why Not Just Use Python?

You should, if you can. Python's `sqlite3` module with `?` placeholders is cleaner:

```python
conn.execute("INSERT INTO users (bio) VALUES (?)", (bio,))
```

But sometimes you're in a context where shelling out to Python is awkward—maybe you're in a CI pipeline, or a minimal container, or you just have a 20-line bash script and don't want to rewrite it. This pattern gives you safe parameterization without leaving bash.

## The Meta-Point

This pattern works because it identifies a quotation boundary that's well-defined on both sides:

- jq knows exactly how to produce a valid JSON string
- sqlite3's `.param` with double quotes parses a compatible format
- The double-encoding bridges any gaps between them

When you're mixing languages or tools, finding these clean boundaries—where one tool's output format is another's input format—is often the key to avoiding escaping nightmares.

---

*This pattern emerged from a conversation about sqlite3 best practices. It's not something I've seen documented elsewhere, which either means it's a genuine discovery or there's a gotcha I haven't hit yet. If you find one, I'd be interested to hear about it.*
