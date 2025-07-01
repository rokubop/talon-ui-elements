import json
import os
import re
from dataclasses import dataclass
from talon import app

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __eq__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __gt__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    @classmethod
    def from_string(cls, version: str) -> "Version":
        major, minor, patch = map(int, version.split("."))
        return cls(major, minor, patch)

    @classmethod
    def from_dict(cls, version: dict) -> "Version":
        return cls(version["major"], version["minor"], version["patch"])

    def to_dict(self) -> dict:
        return {"major": self.major, "minor": self.minor, "patch": self.patch}

# =============================================================================
# UI ELEMENTS PACKAGE VERSION
# =============================================================================

def get_version() -> Version:
    """Get the version of this UI elements library from manifest.json"""
    manifest = os.path.join(os.path.dirname(__file__), '..', 'manifest.json')
    with open(manifest, 'r') as file:
        data = json.load(file)
    return Version.from_string(data['version'])

# =============================================================================
# TALON BREAKING UI VERSION
# =============================================================================

def is_beta_version() -> bool:
    """Check if running on Talon beta branch"""
    try:
        return app.branch.lower() == "beta"
    except Exception:
        return False

def get_talon_version_string() -> str:
    """Get the raw Talon version string"""
    try:
        return app.version
    except Exception:
        return "unknown"

# Cached version to avoid re-evaluation
_talon_breaking_ui_version = None

def talon_breaking_ui_version() -> int:
    """
    v (talon version) - changes
    1 (< 0.4.0-922)
    2 (>= 0.4.0-922)
      - stroke_cap, stroke_join values changed from int to Enum
      - antialias True required
      - int casting required for Surface width and height
    """
    global _talon_breaking_ui_version
    if _talon_breaking_ui_version is None:
        _talon_breaking_ui_version = _evaluate_breaking_version_number()
    return _talon_breaking_ui_version

def _evaluate_breaking_version_number() -> int:
    """Internal function to determine Talon UI API breaking version"""
    v = 2  # default to new version

    # app.version example = "0.4.0-922-bd66"
    try:
        match = re.match(r"(\d+)\.(\d+)\.(\d+)-(\d+)", app.version)
        if match:
            major, minor, patch, build = match.groups()
            # Check if less than 0.4.0-931
            if (int(major), int(minor), int(patch), int(build)) < (0, 4, 0, 931):
                v = 1
    except Exception as e:
        print(f"ui_elements: Error evaluating Talon breaking version: {e}")
        v = 1  # fallback to legacy version on error

    return v
