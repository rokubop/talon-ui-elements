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

font_aliases = {
    "consolas": ["consola", "consolas"],
    "menlo": ["menlo"],
    "courier new": ["cour", "courier"],
}

font_cache = {}

def find_installed_font(font_family: str, font_weight: str = None) -> str | None:
    system = platform.system()
    font_family_key = font_family.lower()
    font_weight = font_weight.lower() if font_weight else None
    search_dirs = []

    if system == "Windows":
        search_dirs = [
            r"C:\Windows\Fonts",  # system
            os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Fonts"),  # user
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

    aliases = font_aliases.get(font_family_key, [font_family_key])
    candidates = []

    for dir_path in search_dirs:
        if not os.path.isdir(dir_path):
            continue
        for file_name in os.listdir(dir_path):
            lower = file_name.lower()
            if any(alias in lower for alias in aliases) and lower.endswith((".ttf", ".otf", ".ttc")):
                candidates.append((file_name, os.path.join(dir_path, file_name)))

    # Prefer exact matches
    weights = weight_keywords.get(font_weight, [font_weight])
    for keyword in weights:
        for name, path in candidates:
            if keyword and keyword in name.lower():
                return path

    # Fall back to any "regular"-ish file
    for name, path in candidates:
        if "regular" in name.lower() or "-" not in name.lower():
            return path

    return candidates[0][1] if candidates else None

def get_typeface(font_family: str, font_weight: str = None) -> Typeface:
    if font_family in font_cache:
        return font_cache[font_family]

    font_path = find_installed_font(font_family, font_weight)
    if font_path:
        typeface = Typeface.from_file(font_path)
        font_cache[font_family] = typeface
        return typeface

    print(f"{font_family} font not found on this system.")
    return None
