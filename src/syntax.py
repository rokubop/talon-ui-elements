import re

# Token types
TOKEN_KEYWORD = "keyword"
TOKEN_STRING = "string"
TOKEN_COMMENT = "comment"
TOKEN_NUMBER = "number"
TOKEN_DECORATOR = "decorator"
TOKEN_BUILTIN = "builtin"
TOKEN_FUNCTION = "function"
TOKEN_OPERATOR = "operator"
TOKEN_PUNCTUATION = "punctuation"
TOKEN_TYPE = "type"
TOKEN_CONSTANT = "constant"
TOKEN_ACTION = "action"
TOKEN_TAG = "tag"
TOKEN_SETTING = "setting"
TOKEN_CAPTURE = "capture"
TOKEN_KEY_BINDING = "key_binding"
TOKEN_CONTEXT_HEADER = "context_header"
TOKEN_TEXT = "text"
TOKEN_DIFF_ADD = "diff_add"
TOKEN_DIFF_ADD_BG = "diff_add_bg"
TOKEN_DIFF_REMOVE = "diff_remove"
TOKEN_DIFF_REMOVE_BG = "diff_remove_bg"
TOKEN_DIFF_HUNK = "diff_hunk"
TOKEN_DIFF_HUNK_BG = "diff_hunk_bg"

# Monokai Pro theme (default)
THEME_MONOKAI = {
    TOKEN_KEYWORD: "FF6188",
    TOKEN_STRING: "FFD866",
    TOKEN_COMMENT: "939293",
    TOKEN_NUMBER: "AB9DF2",
    TOKEN_DECORATOR: "A9DC76",
    TOKEN_BUILTIN: "78DCE8",
    TOKEN_FUNCTION: "A9DC76",
    TOKEN_OPERATOR: "FF6188",
    TOKEN_PUNCTUATION: "FCFCFA",
    TOKEN_TYPE: "78DCE8",
    TOKEN_CONSTANT: "AB9DF2",
    TOKEN_ACTION: "A9DC76",
    TOKEN_TAG: "FCFCFA",
    TOKEN_SETTING: "FCFCFA",
    TOKEN_CAPTURE: "78DCE8",
    TOKEN_KEY_BINDING: "FFD866",
    TOKEN_CONTEXT_HEADER: "FF6188",
    TOKEN_TEXT: "FCFCFA",
    TOKEN_DIFF_ADD: "A9DC76",
    TOKEN_DIFF_ADD_BG: "2EA04330",
    TOKEN_DIFF_REMOVE: "FF6188",
    TOKEN_DIFF_REMOVE_BG: "F8514930",
    TOKEN_DIFF_HUNK: "78DCE8",
    TOKEN_DIFF_HUNK_BG: "78DCE820",
}

# VS Code Dark+ theme
THEME_VSCODE_DARK = {
    TOKEN_KEYWORD: "C586C0",
    TOKEN_STRING: "CE9178",
    TOKEN_COMMENT: "6A9955",
    TOKEN_NUMBER: "B5CEA8",
    TOKEN_DECORATOR: "DCDCAA",
    TOKEN_BUILTIN: "4EC9B0",
    TOKEN_FUNCTION: "DCDCAA",
    TOKEN_OPERATOR: "D4D4D4",
    TOKEN_PUNCTUATION: "D4D4D4",
    TOKEN_TYPE: "4EC9B0",
    TOKEN_CONSTANT: "4FC1FF",
    TOKEN_ACTION: "DCDCAA",
    TOKEN_TAG: "9CDCFE",
    TOKEN_SETTING: "9CDCFE",
    TOKEN_CAPTURE: "4EC9B0",
    TOKEN_KEY_BINDING: "CE9178",
    TOKEN_CONTEXT_HEADER: "569CD6",
    TOKEN_TEXT: "D4D4D4",
    TOKEN_DIFF_ADD: "6A9955",
    TOKEN_DIFF_ADD_BG: "2EA04330",
    TOKEN_DIFF_REMOVE: "F44747",
    TOKEN_DIFF_REMOVE_BG: "F4474730",
    TOKEN_DIFF_HUNK: "569CD6",
    TOKEN_DIFF_HUNK_BG: "569CD620",
}

# Dracula theme
THEME_DRACULA = {
    TOKEN_KEYWORD: "FF79C6",
    TOKEN_STRING: "F1FA8C",
    TOKEN_COMMENT: "6272A4",
    TOKEN_NUMBER: "BD93F9",
    TOKEN_DECORATOR: "50FA7B",
    TOKEN_BUILTIN: "8BE9FD",
    TOKEN_FUNCTION: "50FA7B",
    TOKEN_OPERATOR: "FF79C6",
    TOKEN_PUNCTUATION: "F8F8F2",
    TOKEN_TYPE: "8BE9FD",
    TOKEN_CONSTANT: "BD93F9",
    TOKEN_ACTION: "50FA7B",
    TOKEN_TAG: "F8F8F2",
    TOKEN_SETTING: "F8F8F2",
    TOKEN_CAPTURE: "8BE9FD",
    TOKEN_KEY_BINDING: "F1FA8C",
    TOKEN_CONTEXT_HEADER: "FF79C6",
    TOKEN_TEXT: "F8F8F2",
    TOKEN_DIFF_ADD: "50FA7B",
    TOKEN_DIFF_ADD_BG: "50FA7B30",
    TOKEN_DIFF_REMOVE: "FF5555",
    TOKEN_DIFF_REMOVE_BG: "FF555530",
    TOKEN_DIFF_HUNK: "8BE9FD",
    TOKEN_DIFF_HUNK_BG: "8BE9FD20",
}

# One Dark (Atom) theme
THEME_ONE_DARK = {
    TOKEN_KEYWORD: "C678DD",
    TOKEN_STRING: "98C379",
    TOKEN_COMMENT: "5C6370",
    TOKEN_NUMBER: "D19A66",
    TOKEN_DECORATOR: "E5C07B",
    TOKEN_BUILTIN: "56B6C2",
    TOKEN_FUNCTION: "61AFEF",
    TOKEN_OPERATOR: "56B6C2",
    TOKEN_PUNCTUATION: "ABB2BF",
    TOKEN_TYPE: "56B6C2",
    TOKEN_CONSTANT: "D19A66",
    TOKEN_ACTION: "61AFEF",
    TOKEN_TAG: "ABB2BF",
    TOKEN_SETTING: "ABB2BF",
    TOKEN_CAPTURE: "56B6C2",
    TOKEN_KEY_BINDING: "98C379",
    TOKEN_CONTEXT_HEADER: "C678DD",
    TOKEN_TEXT: "ABB2BF",
    TOKEN_DIFF_ADD: "98C379",
    TOKEN_DIFF_ADD_BG: "98C37930",
    TOKEN_DIFF_REMOVE: "E06C75",
    TOKEN_DIFF_REMOVE_BG: "E06C7530",
    TOKEN_DIFF_HUNK: "61AFEF",
    TOKEN_DIFF_HUNK_BG: "61AFEF20",
}

# GitHub Light theme
THEME_GITHUB_LIGHT = {
    TOKEN_KEYWORD: "CF222E",
    TOKEN_STRING: "0A3069",
    TOKEN_COMMENT: "6E7781",
    TOKEN_NUMBER: "0550AE",
    TOKEN_DECORATOR: "8250DF",
    TOKEN_BUILTIN: "0550AE",
    TOKEN_FUNCTION: "8250DF",
    TOKEN_OPERATOR: "CF222E",
    TOKEN_PUNCTUATION: "24292F",
    TOKEN_TYPE: "0550AE",
    TOKEN_CONSTANT: "0550AE",
    TOKEN_ACTION: "8250DF",
    TOKEN_TAG: "24292F",
    TOKEN_SETTING: "24292F",
    TOKEN_CAPTURE: "0550AE",
    TOKEN_KEY_BINDING: "0A3069",
    TOKEN_CONTEXT_HEADER: "CF222E",
    TOKEN_TEXT: "24292F",
    TOKEN_DIFF_ADD: "116329",
    TOKEN_DIFF_ADD_BG: "CCFFD830",
    TOKEN_DIFF_REMOVE: "82071E",
    TOKEN_DIFF_REMOVE_BG: "FFD7D530",
    TOKEN_DIFF_HUNK: "0550AE",
    TOKEN_DIFF_HUNK_BG: "DDF4FF30",
}

DEFAULT_THEME = THEME_MONOKAI


def _build_python_patterns():
    keywords = (
        r'\b(?:False|None|True|and|as|assert|async|await|break|class|continue|'
        r'def|del|elif|else|except|finally|for|from|global|if|import|in|is|'
        r'lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b'
    )
    builtins = (
        r'\b(?:print|len|range|int|str|float|list|dict|set|tuple|bool|type|'
        r'isinstance|issubclass|hasattr|getattr|setattr|delattr|callable|'
        r'super|property|staticmethod|classmethod|enumerate|zip|map|filter|'
        r'sorted|reversed|any|all|min|max|sum|abs|round|open|input|format|'
        r'repr|id|hash|iter|next|vars|dir|help|Exception|ValueError|'
        r'TypeError|KeyError|IndexError|AttributeError|RuntimeError|'
        r'StopIteration|NotImplementedError|OSError|IOError)\b'
    )
    constants = r'\b(?:True|False|None)\b'

    return [
        (TOKEN_COMMENT, re.compile(r'#.*$')),
        (TOKEN_STRING, re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')),
        (TOKEN_DECORATOR, re.compile(r'@[\w.]+')),
        (TOKEN_CONSTANT, re.compile(constants)),
        (TOKEN_NUMBER, re.compile(r'\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b', re.IGNORECASE)),
        (TOKEN_KEYWORD, re.compile(keywords)),
        (TOKEN_FUNCTION, re.compile(r'\b(\w+)(?=\s*\()')),
        (TOKEN_BUILTIN, re.compile(builtins)),
        (TOKEN_OPERATOR, re.compile(r'[+\-*/%=<>!&|^~]+')),
        (TOKEN_PUNCTUATION, re.compile(r'[(){}\[\]:;,.]')),
    ]


def _build_talon_patterns():
    return [
        (TOKEN_COMMENT, re.compile(r'#.*$')),
        (TOKEN_STRING, re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')),
        (TOKEN_KEY_BINDING, re.compile(r'key\([^)]*\)')),
        (TOKEN_CONTEXT_HEADER, re.compile(r'^(?:app|mode|tag|title|os|language|hostname)\b.*:', re.MULTILINE)),
        (TOKEN_CAPTURE, re.compile(r'<[^>]+>')),
        (TOKEN_ACTION, re.compile(r'(?:user\.\w+|self\.\w+|[\w.]+)\s*(?=\()')),
        (TOKEN_NUMBER, re.compile(r'\b\d+(?:\.\d+)?\b')),
        (TOKEN_SETTING, re.compile(r'^\s*(?:user\.)\w+', re.MULTILINE)),
        (TOKEN_OPERATOR, re.compile(r'[=:+\-*/]')),
        (TOKEN_PUNCTUATION, re.compile(r'[(){}\[\],.]')),
    ]


_THEME_REGISTRY = {
    "monokai": THEME_MONOKAI,
    "vscode_dark": THEME_VSCODE_DARK,
    "dracula": THEME_DRACULA,
    "one_dark": THEME_ONE_DARK,
    "github_light": THEME_GITHUB_LIGHT,
}

_LANGUAGE_PATTERNS = {
    "python": _build_python_patterns(),
    "talon": _build_talon_patterns(),
}


def register_theme(name, theme):
    """Register a named code theme.
    theme: dict mapping token types to hex color strings."""
    _THEME_REGISTRY[name] = theme


def resolve_theme(theme):
    """Resolve a theme - string name, dict, or None to a theme dict."""
    if theme is None:
        return DEFAULT_THEME
    if isinstance(theme, dict):
        return theme
    if isinstance(theme, str):
        resolved = _THEME_REGISTRY.get(theme)
        if resolved:
            return resolved
        print(f"Unknown code theme '{theme}'. Available: {', '.join(sorted(_THEME_REGISTRY.keys()))}")
        return DEFAULT_THEME
    return DEFAULT_THEME


def register_language(name, patterns):
    """Register a custom language for syntax highlighting.
    patterns: list of (token_type, compiled_regex) tuples, ordered by priority."""
    _LANGUAGE_PATTERNS[name] = patterns


def tokenize_line(line, language="python"):
    """Tokenize a single line of code into (text, token_type) tuples."""
    patterns = _LANGUAGE_PATTERNS.get(language, _LANGUAGE_PATTERNS["python"])
    tokens = []
    pos = 0

    while pos < len(line):
        best_match = None
        best_token_type = None
        best_start = len(line)

        for token_type, pattern in patterns:
            match = pattern.search(line, pos)
            if match and match.start() < best_start:
                best_start = match.start()
                best_match = match
                best_token_type = token_type

        if best_match is None:
            tokens.append((line[pos:], TOKEN_TEXT))
            break

        if best_start > pos:
            tokens.append((line[pos:best_start], TOKEN_TEXT))

        matched_text = best_match.group()
        # For function pattern, we captured group(1) but want full match position
        if best_token_type == TOKEN_FUNCTION and best_match.lastindex:
            matched_text = best_match.group(1)
            tokens.append((matched_text, best_token_type))
            pos = best_match.start() + len(matched_text)
        else:
            tokens.append((matched_text, best_token_type))
            pos = best_match.end()

    return tokens


_TRIPLE_QUOTE_LANGS = {"python"}


def _tokenize_python_with_triple_quotes(lines):
    """Python tokenizer that tracks triple-quoted strings across line
    boundaries. Once a `\"\"\"` or `'''` opens on one line and doesn't close
    on the same line, every subsequent line stays inside the string until
    the matching closer appears. Without this, content inside multi-line
    strings gets re-tokenized as code (so `and` reads as a keyword, slashes
    as operators), and the trailing closer renders as a stray `\"`."""
    result = []
    pending = None  # The marker we're inside ('\"\"\"' or '\'\'\''), or None.

    for line in lines:
        if pending is not None:
            close_idx = line.find(pending)
            if close_idx < 0:
                # Whole line is still inside the string.
                result.append([(line, TOKEN_STRING)] if line else [])
                continue
            # Closer found. Everything up through it is string; tokenize the
            # tail (if any) as code.
            str_part = line[: close_idx + 3]
            rest = line[close_idx + 3 :]
            tokens = [(str_part, TOKEN_STRING)]
            if rest:
                tokens.extend(tokenize_line(rest, "python"))
            result.append(tokens)
            pending = None
            continue

        # Not currently inside a multi-line string. Look for an opener that
        # has no matching closer later on the same line — that's the start
        # of a multi-line string.
        opener_idx = -1
        opener_marker = None
        for marker in ('"""', "'''"):
            search_from = 0
            while True:
                open_idx = line.find(marker, search_from)
                if open_idx < 0:
                    break
                close_idx = line.find(marker, open_idx + 3)
                if close_idx < 0:
                    # Opens but doesn't close on this line.
                    if opener_idx < 0 or open_idx < opener_idx:
                        opener_idx = open_idx
                        opener_marker = marker
                    break
                # Same-line pair; skip past it and keep scanning.
                search_from = close_idx + 3

        if opener_marker is None:
            result.append(tokenize_line(line, "python"))
        else:
            head = line[:opener_idx]
            tail_string = line[opener_idx:]
            tokens = tokenize_line(head, "python") if head else []
            tokens.append((tail_string, TOKEN_STRING))
            result.append(tokens)
            pending = opener_marker

    return result


def tokenize(text, language="python"):
    """Tokenize multi-line code text. Returns list of list of (text, token_type) per line."""
    lines = text.split("\n")
    if language in _TRIPLE_QUOTE_LANGS:
        return _tokenize_python_with_triple_quotes(lines)
    return [tokenize_line(line, language) for line in lines]
