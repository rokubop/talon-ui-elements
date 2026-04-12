# Code Element - Diff Mode

`diff=True` is an overlay on top of normal syntax highlighting. It parses diff prefixes (`+`, `-`, `@@`, space) per line, draws colored line backgrounds, then syntax-highlights the remaining content using the specified `language`.

## Usage

```python
diff_text = """\
@@ -10,6 +10,8 @@
 def hello():
-    print("old")
+    print("new")
+    print("added")
     return True"""

code(diff_text, language="python", diff=True)
```

- `+` lines get green background
- `-` lines get red background
- `@@` lines get blue/cyan background
- Context lines (space prefix) render normally

The `language` param still controls syntax highlighting on the code content after stripping the prefix.

## Theme Keys

Diff colors are part of each built-in theme and customizable:

| Key | Purpose |
|-----|---------|
| `diff_add` | Text color for `+` prefix |
| `diff_add_bg` | Background color for added lines |
| `diff_remove` | Text color for `-` prefix |
| `diff_remove_bg` | Background color for removed lines |
| `diff_hunk` | Text color for `@@` lines |
| `diff_hunk_bg` | Background color for `@@` lines |

```python
code(diff_text, language="python", diff=True, theme={
    "diff_add": "50FA7B",
    "diff_add_bg": "50FA7B30",
    "diff_remove": "FF5555",
    "diff_remove_bg": "FF555530",
    "keyword": "FF79C6",
    # ...other syntax tokens
})
```
