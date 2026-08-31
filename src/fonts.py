import os
import platform
from talon import settings
from talon.skia.typeface import Typeface

# Talon's Skia binding predates SkFont::setEdging, so there is no `edging`
# property to set -- the knobs are the older SkPaint text flags plus a couple
# on paint.font. FontHinting is exported by the native skia module; guard the
# import so a build without it degrades to "leave hinting alone".
try:
    from skia import FontHinting
except Exception:
    FontHinting = None

# Weight names used internally. Consumer-facing values (CSS keywords and
# numeric weights) are normalized onto these by _normalize_weight.
_WEIGHT_ALIASES = {
    "": "regular", "normal": "regular", "book": "regular", "roman": "regular",
    "thin": "light", "extralight": "light", "ultralight": "light",
    "demibold": "semibold",
    "extrabold": "bold", "ultrabold": "bold",
    "heavy": "black",
    "100": "light", "200": "light", "300": "light", "400": "regular",
    "500": "medium", "600": "semibold", "700": "bold", "800": "bold",
    "900": "black",
}

# Light to heavy. Used to decide whether the face we settled for is heavy
# enough to stand in for the weight that was asked for.
_WEIGHT_ORDER = {
    "light": 0, "semilight": 1, "regular": 2, "medium": 3,
    "semibold": 4, "bold": 5, "black": 6,
}

# What to settle for when the requested weight has no face on disk, best
# substitute first.
_WEIGHT_FALLBACKS = {
    "regular": ["regular", "medium", "light", "semilight", "semibold", "bold", "black"],
    "medium": ["medium", "regular", "semibold", "light", "semilight", "bold", "black"],
    "light": ["light", "semilight", "regular", "medium", "semibold", "bold", "black"],
    "semilight": ["semilight", "light", "regular", "medium", "semibold", "bold", "black"],
    "semibold": ["semibold", "bold", "medium", "black", "regular", "light", "semilight"],
    "bold": ["bold", "semibold", "black", "medium", "regular", "light", "semilight"],
    "black": ["black", "bold", "semibold", "medium", "regular", "light", "semilight"],
}

# Windows names faces by appending a terse code to the family stem rather
# than spelling the style out: arial/arialbd/ariali/arialbi,
# segoeui/segoeuib/segoeuii/segoeuiz, consola/consolab/consolai/consolaz.
# Nothing in those names contains the word "bold", so a keyword search over
# the filename never finds a real bold face on Windows.
_SUFFIX_STYLES = {
    "": ("regular", False),
    "r": ("regular", False),
    "ri": ("regular", True),
    "i": ("regular", True),
    "it": ("regular", True),
    "m": ("medium", False),
    "mi": ("medium", True),
    "b": ("bold", False),
    "bd": ("bold", False),
    "bi": ("bold", True),
    "z": ("bold", True),
    "l": ("light", False),
    "li": ("light", True),
    "sb": ("semibold", False),
    "sbi": ("semibold", True),
    "sl": ("semilight", False),
    "sli": ("semilight", True),
    "bl": ("black", False),
    "bli": ("black", True),
    "bk": ("black", False),
}

# Mac and Linux spell the style out instead (Roboto-Bold, DejaVuSans-BoldOblique).
# Longest first: "semibold" and "extralight" must be consumed before "bold"
# and "light" can match inside them.
_DESCRIPTIVE_STYLES = [
    ("semibold", "semibold"), ("demibold", "semibold"),
    ("extrabold", "bold"), ("ultrabold", "bold"),
    ("extralight", "light"), ("ultralight", "light"),
    ("semilight", "semilight"),
    ("black", "black"), ("heavy", "black"),
    ("bold", "bold"),
    ("medium", "medium"),
    ("light", "light"), ("thin", "light"),
    ("regular", "regular"), ("normal", "regular"), ("book", "regular"),
]
_DESCRIPTIVE_ITALIC = ("italic", "oblique")

# What a font file puts between the family stem and the style text.
_NAME_SEPARATORS = "-_. "

FONT_EXTENSIONS = (".ttf", ".otf", ".ttc")

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

# Filename stems that hold more faces of a family whose main stem is the key.
# Windows splits Segoe UI in two: segoeui* carries regular/bold/italic/light,
# while semibold, black and semilight sit under segui*. They are one family,
# so they're scanned as one candidate pool rather than as competing aliases.
related_stems = {
    "segoeui": ["segui"],
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

def _normalize_weight(font_weight) -> str:
    if font_weight is None:
        return "regular"
    key = str(font_weight).strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    return _WEIGHT_ALIASES.get(key, key or "regular")


def _normalize_name(name: str) -> str:
    """Font family names are written with spaces and underscores; filenames
    aren't. Compare on a form that ignores the difference."""
    return name.lower().replace(" ", "").replace("_", "")


def _classify_suffix(suffix: str):
    """(weight, italic, explicit) for the part of a filename that follows the
    family stem, or None when the suffix isn't a style marker at all.

    None means the file is a *different* family that merely shares a prefix,
    so it must not be offered as a face of the requested one -- the "cour"
    alias for Courier New otherwise picks up Courgette-Regular.ttf, and
    "arial" picks up Arial Narrow.

    `explicit` is False when the suffix is accepted but names no style
    (Figerona-VF.ttf), so a sibling that does name one wins the tie.
    """
    if suffix in _SUFFIX_STYLES:
        weight, italic = _SUFFIX_STYLES[suffix]
        return (weight, italic, True)

    # A separator right after the family stem means everything past it is
    # style or variant text, however it's spelled: Inter-Bold-slnt=0,
    # Bison-Bold(PersonalUse). Without one, the suffix has to be spelled
    # entirely out of style words or it belongs to another family.
    after_separator = suffix[:1] in _NAME_SEPARATORS and suffix != ""

    if after_separator:
        # Ubuntu-B.ttf, Ubuntu-RI.ttf: the terse code, separated.
        code = suffix.lstrip(_NAME_SEPARATORS)
        if code in _SUFFIX_STYLES:
            weight, italic = _SUFFIX_STYLES[code]
            return (weight, italic, True)

    rest = suffix
    italic = False
    weight = None
    for keyword in _DESCRIPTIVE_ITALIC:
        if keyword in rest:
            rest = rest.replace(keyword, "", 1)
            italic = True
            break
    for keyword, keyword_weight in _DESCRIPTIVE_STYLES:
        if keyword in rest:
            rest = rest.replace(keyword, "", 1)
            weight = keyword_weight
            break

    named_a_style = weight is not None or italic
    if not after_separator and (rest.strip(_NAME_SEPARATORS) or not named_a_style):
        return None
    return (weight or "regular", italic, named_a_style)


def _scan_candidates(alias: str, search_dirs: list) -> list:
    """Every installed face of one family alias, as (weight, italic, path).
    Faces that name their style sort ahead of ones that don't."""
    found = []
    for dir_path in search_dirs:
        if not os.path.isdir(dir_path):
            continue
        for file_name in os.listdir(dir_path):
            lower = file_name.lower()
            if not lower.endswith(FONT_EXTENSIONS):
                continue
            base = _normalize_name(os.path.splitext(lower)[0])
            if not base.startswith(alias):
                continue
            style = _classify_suffix(base[len(alias):])
            if style is None:
                continue
            found.append((style[2], style[0], style[1], os.path.join(dir_path, file_name)))
    found.sort(key=lambda entry: not entry[0])
    return [(weight, italic, path) for _, weight, italic, path in found]


def resolve_installed_font(
    font_family: str, font_weight: str = None, font_style: str = None
):
    """Pick the installed face that best matches family + weight + style.

    Returns (path, weight, italic) for the face actually chosen, or None.
    The resolved weight is not necessarily the requested one -- callers use
    it to decide whether they still need to synthesize bold or italic.
    """
    aliases = font_aliases.get(font_family.lower(), [font_family])
    aliases = [_normalize_name(alias) for alias in aliases]
    want_weight = _normalize_weight(font_weight)
    want_italic = str(font_style or "").lower() == "italic"
    search_dirs = get_font_dirs()

    log(f"Finding font: family='{font_family}', weight='{want_weight}', italic={want_italic}")
    log(f"Resolved aliases: {aliases}")

    # Aliases are a priority list, so an earlier alias with any usable face
    # always beats a later one. Scanning them as one pool is what let
    # font_family="sans-serif" with font_weight="bold" resolve to
    # UbuntuMono-Bold: the keyword search found "bold" in a later alias
    # before it found Segoe UI at all.
    for alias in aliases:
        candidates = _scan_candidates(alias, search_dirs)
        for stem in related_stems.get(alias, []):
            candidates += _scan_candidates(stem, search_dirs)
        if not candidates:
            continue
        log(f"  alias '{alias}' candidates: {candidates}")
        for weight in _WEIGHT_FALLBACKS.get(want_weight, [want_weight, "regular"]):
            for italic in ([True, False] if want_italic else [False, True]):
                for cand_weight, cand_italic, path in candidates:
                    if cand_weight == weight and cand_italic == italic:
                        log(f"  match: {path} ({weight}, italic={italic})")
                        return (path, weight, italic)

    return None


def find_installed_font(font_family: str, font_weight: str = None, font_style: str = None) -> str | None:
    match = resolve_installed_font(font_family, font_weight, font_style)
    return match[0] if match else None


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


class ResolvedFont:
    """A loaded typeface plus what the renderer still has to fake.

    Talon can only synthesize bold (paint.font.embolden) and italic
    (paint.font.skew_x). Both look visibly weaker than a real face, so they
    are only worth applying when the face on disk doesn't already provide
    the weight or slant that was asked for.
    """

    __slots__ = ("typeface", "weight", "italic", "synthetic_bold", "synthetic_italic")

    def __init__(self, typeface, weight, italic, want_weight, want_italic):
        self.typeface = typeface
        self.weight = weight
        self.italic = italic
        # Fake bold whenever a heavy weight was asked for and nothing heavy
        # came back. Previously this only fired for font_weight="bold", so
        # "semibold" and "black" silently rendered at regular weight.
        wanted = _WEIGHT_ORDER.get(want_weight, 2)
        got = _WEIGHT_ORDER.get(weight, 2)
        self.synthetic_bold = wanted >= _WEIGHT_ORDER["semibold"] and got <= _WEIGHT_ORDER["regular"]
        self.synthetic_italic = want_italic and not italic


def resolve_font(
    font_family: str, font_weight: str = None, font_style: str = None
) -> ResolvedFont:
    """Load the best face for family/weight/style and report what's left to
    fake. Always returns a ResolvedFont; `.typeface` is None when nothing
    could be loaded and the caller should keep Talon's default face."""
    want_weight = _normalize_weight(font_weight)
    want_italic = str(font_style or "").lower() == "italic"

    if not font_family:
        return ResolvedFont(None, "regular", False, want_weight, want_italic)

    key = (font_family, font_weight, font_style)
    if key in font_cache:
        return font_cache[key]

    def _resolved(typeface, weight, italic):
        resolved = ResolvedFont(typeface, weight, italic, want_weight, want_italic)
        font_cache[key] = resolved
        return resolved

    match = resolve_installed_font(font_family, font_weight, font_style)
    log("Found font match:", match)
    if match:
        typeface = _try_load_typeface(match[0])
        if typeface is not None:
            return _resolved(typeface, match[1], match[2])

    # Try platform equivalents before giving up
    for equivalent in platform_equivalents.get(font_family.lower(), []):
        log(f"Trying platform equivalent: {equivalent}")
        equiv = resolve_installed_font(equivalent, font_weight, font_style)
        if equiv:
            typeface = _try_load_typeface(equiv[0])
            if typeface is not None:
                print(f"Font '{font_family}' not found, using platform equivalent '{equivalent}'")
                return _resolved(typeface, equiv[1], equiv[2])

    # Only log the error once per font to avoid console spam
    if font_family not in _logged_font_errors:
        _logged_font_errors.add(font_family)
        print(f"Font '{font_family}' not found. Use one of:")
        for font in list_available_fonts():
            print("  ", font)
    # Cache the miss so we don't redo all that scanning on every render.
    return _resolved(None, "regular", False)


def get_typeface(font_family: str, font_weight: str = None, font_style: str = None) -> Typeface:
    return resolve_font(font_family, font_weight, font_style).typeface


# populated by node_text; cleared on font reset so fallback-typeface
# measurements don't survive a font retry
line_height_cache = {}
text_width_cache = {}
TEXT_WIDTH_CACHE_MAX = 4096

SETTING_SUBPIXEL = "user.ui_elements_text_subpixel"
SETTING_HINTING = "user.ui_elements_text_hinting"

_logged_paint_errors = set()


def _set_paint_attr(target, attr, value, label):
    """Set one rendering flag, tolerating a Talon build that lacks it. A
    missing knob must degrade the look, never break the render."""
    try:
        setattr(target, attr, value)
    except Exception:
        if label not in _logged_paint_errors:
            _logged_paint_errors.add(label)
            print(f"ui_elements: this Talon build has no {label}, skipping it")


def apply_text_rendering(paint):
    """Apply the global text rendering settings to a text paint.

    Text is drawn with the paint passed to c.draw_text, not with c.paint, so
    every place that builds its own Paint for text has to go through here or
    it silently renders with Skia's defaults.

    Only two knobs in Talon's Skia actually change rasterized glyphs. Measured
    against pixel hashes on this build, `antialias` and `lcd_render_text` are
    inert for text (Talon builds the font separately from the paint, and this
    Skia predates SkFont::setEdging), and `hinting` is really a two-state
    toggle -- SLIGHT, NORMAL and FULL all rasterize identically. antialias is
    still set unconditionally because node_input_text and node_textarea have
    always set it and it costs nothing.
    """
    _set_paint_attr(paint, "antialias", True, "paint.antialias")
    _set_paint_attr(
        paint.font, "subpixel",
        bool(settings.get(SETTING_SUBPIXEL, True)),
        "paint.font.subpixel",
    )

    hinting = str(settings.get(SETTING_HINTING, "") or "").strip().upper()
    if hinting:
        value = getattr(FontHinting, hinting, None) if FontHinting else None
        if value is None:
            if hinting not in _logged_paint_errors:
                _logged_paint_errors.add(hinting)
                print(
                    f"ui_elements: unknown text hinting '{hinting}'. "
                    "Use none, slight, normal or full."
                )
        else:
            _set_paint_attr(paint, "hinting", value, "paint.hinting")


def reset_font_state():
    """Reset logged font errors so they can be shown again. Called by store.clear()."""
    global _logged_font_errors
    _logged_font_errors.clear()
    _logged_paint_errors.clear()
    # drop negative entries so failed fonts actually retry; keep loaded typefaces
    for key in [k for k, v in font_cache.items() if v is None or v.typeface is None]:
        del font_cache[key]
    line_height_cache.clear()
    text_width_cache.clear()
