import os
import platform
from talon.skia.typeface import Typeface

weight_keywords = {
    "regular": ["regular", ""],
    "light": ["light", "thin", "extralight"],
    "medium": ["medium"],
    "semibold": ["semibold", "demibold"],
    "bold": ["bold", "extrabold", "heavy"],
    "black": ["black"],
}

preferred_weights = ["regular", "", "medium", "light", "semibold", "bold", "black"]

font_aliases = {
    "consolas": ["consola", "consolas"],
    "menlo": ["menlo"],
    "courier new": ["cour", "courier"],
    "courier_new": ["cour", "courier"],
    "comic sans ms": ["comic", "comicz"],
    "comic_sans_ms": ["comic", "comicz"],
    # Add monospace support with prioritized common monospace fonts
    "monospace": [
        "consola", "consolas", "menlo", "dejavu sans mono", "liberation mono", "courier new", "monaco", "andale mono", "ubuntu mono", "source code pro"
    ],
    "segoe ui": ["segoeui", "segoeuib", "segoeuil", "segoeuisl", "segoeuiz", "segoeuiblack"],
    "segoe_ui": ["segoeui", "segoeuib", "segoeuil", "segoeuisl", "segoeuiz", "segoeuiblack"],
    "times new roman": ["times", "timesnewroman"],
}

font_cache = {}
_logged_font_errors = set()  # Track fonts we've already logged errors for
LOG = False

def log(*args):
    if LOG:
        print("LOG:", *args)

def get_font_dirs():
    system = platform.system()
    search_dirs = []

    if system == "Windows":
        search_dirs = [
            r"C:\Windows\Fonts",
            os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts"),
        ]
    elif system == "Darwin": # mac
        search_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    elif system == "Linux":
        search_dirs = [
            "/usr/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts"),
        ]
    return search_dirs

def list_available_fonts():
    font_dirs = get_font_dirs()
    fonts = set()
    for dir_path in font_dirs:
        if not os.path.isdir(dir_path):
            continue
        for file in os.listdir(dir_path):
            if file.lower().endswith((".ttf", ".otf", ".ttc")):
                fonts.add(file.lower())
    return sorted(fonts)

def find_installed_font(font_family: str, font_weight: str = None) -> str | None:

    font_family_key = font_family.lower()
    font_weight = font_weight.lower() if font_weight else None
    search_dirs = get_font_dirs()

    log(f"Finding font: family='{font_family}', weight='{font_weight}'")
    log(f"Search directories: {search_dirs}")

    aliases = font_aliases.get(font_family_key, [font_family_key])
    log(f"Resolved aliases: {aliases}")
    candidates = []

    for dir_path in search_dirs:
        log(f"Scanning directory: {dir_path}")
        if not os.path.isdir(dir_path):
            log("  Skipped (not a directory)")
            continue
        for file_name in os.listdir(dir_path):
            lower = file_name.lower()
            font_base = lower.replace(".ttf", "").replace(".otf", "").replace(".ttc", "")
            if any(font_base.startswith(alias) for alias in aliases):
                log(f"  Match found: {file_name}")
                candidates.append((file_name, os.path.join(dir_path, file_name)))

    # Prefer exact matches
    log(f"Total candidates found: {len(candidates)}")

    weights = weight_keywords.get(font_weight, [font_weight]) if font_weight else []
    weights += [w for w in preferred_weights if w not in weights]

    for keyword in weights:
        log(f"Looking for keyword: {keyword}")
        for name, path in candidates:
            if keyword and keyword in name.lower():
                log(f"  Weight match: {name}")
                return path

    log("Trying fallback to regular-ish match...")
    for name, path in candidates:
        if "regular" in name.lower() or "-" not in name.lower():
            return path

    return candidates[0][1] if candidates else None

def get_typeface(font_family: str, font_weight: str = None) -> Typeface:
    key = (font_family, font_weight)
    if key in font_cache:
        return font_cache[key]

    font_path = find_installed_font(font_family, font_weight)
    log("Found font path:", font_path)
    if font_path:
        try:
            typeface = Typeface.from_file(font_path, 0)
        except TypeError:
            typeface = Typeface.from_file(font_path)
        font_cache[key] = typeface
        return typeface

    # Only log the error once per font to avoid console spam
    if font_family not in _logged_font_errors:
        _logged_font_errors.add(font_family)
        print(f"Font '{font_family}' not found. Use one of:")
        for font in list_available_fonts():
            print("  ", font)
    return None

def reset_font_state():
    """Reset logged font errors so they can be shown again. Called by store.clear()."""
    global _logged_font_errors
    _logged_font_errors.clear()
