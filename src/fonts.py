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

_SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"


def _by_os(*, windows: list, mac: list, linux: list) -> list:
    """Build an alias list ordered for the current OS first, then fall
    through to the other platforms' fonts so a missing native font (rare
    but possible on stripped systems) still resolves. De-dupes while
    preserving order."""
    if _SYSTEM == "Darwin":
        order = (mac, windows, linux)
    elif _SYSTEM == "Linux":
        order = (linux, mac, windows)
    else:
        order = (windows, mac, linux)
    seen, out = set(), []
    for group in order:
        for name in group:
            if name not in seen:
                seen.add(name)
                out.append(name)
    return out


font_aliases = {
    "consolas": ["consola", "consolas"],
    "menlo": ["menlo"],
    "courier new": ["cour", "courier"],
    "courier_new": ["cour", "courier"],
    "comic sans ms": ["comic", "comicz"],
    "comic_sans_ms": ["comic", "comicz"],
    # CSS generic family names. Each maps to a prioritized list of
    # platform-typical fonts so consumers can write
    # `font_family="serif"` portably; the active OS's fonts are tried
    # first via _by_os so Mac picks Helvetica before Arial, etc.
    "monospace": _by_os(
        windows=["consola", "consolas", "courier new"],
        mac=["menlo", "monaco", "sfmono", "andale mono"],
        linux=[
            "dejavu sans mono", "liberation mono", "ubuntu mono",
            "source code pro",
        ],
    ),
    "serif": _by_os(
        windows=["times", "timesnewroman", "georgia", "cambria", "constantia"],
        mac=["times", "georgia", "cochin", "didot", "baskerville"],
        linux=[
            "dejavu serif", "liberation serif", "noto serif", "freeserif",
        ],
    ),
    "sans-serif": _by_os(
        windows=["segoeui", "arial", "verdana", "tahoma", "calibri"],
        mac=[
            "helvetica", "sfns", "applesystem", "lucidagrande", "arial",
        ],
        linux=[
            "dejavu sans", "liberation sans", "noto sans", "ubuntu",
            "roboto", "cantarell",
        ],
    ),
    "system-ui": _by_os(
        windows=["segoeui"],
        mac=["sfns", "sf pro", "helvetica neue", "helvetica"],
        linux=["cantarell", "ubuntu", "noto sans", "dejavu sans"],
    ),
    "segoe ui": ["segoeui", "segoeuib", "segoeuil", "segoeuisl", "segoeuiz", "segoeuiblack"],
    "segoe_ui": ["segoeui", "segoeuib", "segoeuil", "segoeuisl", "segoeuiz", "segoeuiblack"],
    "times new roman": ["times", "timesnewroman"],
}

# Underscore aliases for the hyphenated CSS names (some consumers can't
# pass hyphens through ui_elements property names).
font_aliases["sans_serif"] = font_aliases["sans-serif"]
font_aliases["system_ui"] = font_aliases["system-ui"]

# Cross-platform font equivalents - ordered by preference
platform_equivalents = {
    # Monospace fonts
    "consolas": ["menlo", "sfnsmono", "monaco", "courier new"],  # Windows -> Mac
    "menlo": ["consolas", "courier new"],  # Mac -> Windows
    "sf mono": ["consolas", "menlo", "courier new"],  # Mac -> Windows/Linux
    "sfnsmono": ["consolas", "menlo", "courier new"],
    "monaco": ["consolas", "menlo", "courier new"],  # Mac -> Windows/Linux

    # Sans-serif fonts
    "segoe ui": ["sfns", "helvetica neue", "arial"],  # Windows -> Mac/Linux
    "segoe_ui": ["sfns", "helvetica neue", "arial"],
    "sf pro": ["segoe ui", "arial"],  # Mac -> Windows/Linux
    "sfns": ["segoe ui", "arial"],
    "helvetica neue": ["segoe ui", "arial"],  # Mac -> Windows/Linux

    # Serif fonts
    "times new roman": ["times", "times new roman"],
    "georgia": ["times", "times new roman"],
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

def _try_load_typeface(font_path: str) -> Typeface | None:
    """Load a Typeface from a path, swallowing any failure. Returns None
    if the file isn't a usable font (corrupt, unsupported format, the
    aliasing glob picked up something that looks like a font but isn't).
    Lets callers fall through to the next fallback instead of crashing
    the whole render."""
    try:
        return Typeface.from_file(font_path, 0)
    except TypeError:
        # Older Talon Typeface.from_file signature (no face_index arg).
        try:
            return Typeface.from_file(font_path)
        except Exception:
            return None
    except Exception:
        return None


def get_typeface(font_family: str, font_weight: str = None) -> Typeface:
    key = (font_family, font_weight)
    if key in font_cache:
        return font_cache[key]

    font_path = find_installed_font(font_family, font_weight)
    log("Found font path:", font_path)
    if font_path:
        typeface = _try_load_typeface(font_path)
        if typeface is not None:
            font_cache[key] = typeface
            return typeface

    # Try platform equivalents before giving up
    equivalents = platform_equivalents.get(font_family.lower(), [])
    for equivalent in equivalents:
        log(f"Trying platform equivalent: {equivalent}")
        equiv_path = find_installed_font(equivalent, font_weight)
        if equiv_path:
            typeface = _try_load_typeface(equiv_path)
            if typeface is not None:
                print(f"Font '{font_family}' not found, using platform equivalent '{equivalent}'")
                font_cache[key] = typeface
                return typeface

    # Only log the error once per font to avoid console spam
    if font_family not in _logged_font_errors:
        _logged_font_errors.add(font_family)
        print(f"Font '{font_family}' not found. Use one of:")
        for font in list_available_fonts():
            print("  ", font)
    # Cache the miss so we don't redo all that scanning on every render.
    font_cache[key] = None
    return None

_paint_cache = {}
_PAINT_CACHE_MAX = 256

# Text measurement caches (populated by node_text). Live here so
# reset_font_state clears them together with the paint cache - measurements
# taken against a fallback typeface must not survive a font retry.
line_height_cache = {}
text_width_cache = {}
TEXT_WIDTH_CACHE_MAX = 4096

def get_text_paint(font_size, font_family, font_weight, font_style="normal") -> "Paint":
    """Shared, cached Paint configured for a font. Callers may set per-use
    fields (color, style, stroke_width) freely - those are reassigned on every
    use - but must restore font fields (e.g. embolden) if they toggle them.
    All canvas draw/measure work happens on Talon's UI thread, so sharing is safe."""
    from talon.skia.paint import Paint
    key = (font_size, font_family, font_weight, font_style)
    paint = _paint_cache.get(key)
    if paint is None:
        paint = Paint()
        paint.textsize = font_size
        if font_family:
            typeface = get_typeface(font_family, font_weight)
            if typeface:
                paint.typeface = typeface
        paint.font.embolden = font_weight == "bold"
        if font_style == "italic":
            paint.font.skew_x = -0.25
        if len(_paint_cache) >= _PAINT_CACHE_MAX:
            _paint_cache.clear()
        _paint_cache[key] = paint
    return paint

def reset_font_state():
    """Reset logged font errors so they can be shown again. Called by store.clear()."""
    global _logged_font_errors
    _logged_font_errors.clear()
    _paint_cache.clear()
    line_height_cache.clear()
    text_width_cache.clear()
