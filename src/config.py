"""
Central configuration loader for youtube-to-knowledge.

Reads config.yaml from the project root (one level above src/).
Falls back to built-in defaults for any missing keys, so the project
works out of the box without a config file.

Usage (in any src/ module):
    from config import cfg
    langs = cfg.transcription.languages
    vault = cfg.vault.base_dir
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# ── Locate config file ─────────────────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"

# ── Built-in defaults ──────────────────────────────────────────────────────────
_DEFAULTS: dict[str, Any] = {
    "vault": {
        "base_dir": "vault",
        "content_dir": "vault/content",
        "db_file": "vault/processed_videos.md",
    },
    "transcription": {
        "languages": ["pl", "en"],
        "audio_format": "m4a/bestaudio/best",
        "default_model": "small",
        "default_engine": "whisper",
    },
    "whisperx": {
        "batch_size": 16,
        "compute_type": "int8",
    },
    "extraction": {
        "default_depth": "standard",
        "depths": {
            "light":    {"takeaways": [3, 5],  "triplets": [8, 12]},
            "standard": {"takeaways": [5, 8],  "triplets": [15, 20]},
            "deep":     {"takeaways": [8, 12], "triplets": [25, 35]},
        },
    },
    "graph": {
        "height": "750px",
        "width": "100%",
        "bgcolor": "#222222",
        "font_color": "white",
    },
    "obsidian": {
        "default_tag": "youtube-to-knowledge",
        "entity_type": "entity",
        "section_headers": {
            "source": "Source",
            "relations": "Relations",
            "referenced_by": "Referenced by",
        },
    },
}


# ── Deep-merge helper ──────────────────────────────────────────────────────────
def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into *base*, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# ── Load & merge ───────────────────────────────────────────────────────────────
def _load() -> dict:
    if _CONFIG_PATH.exists():
        try:
            import yaml  # soft dependency — only needed when config.yaml exists
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f) or {}
            return _deep_merge(_DEFAULTS, user_cfg)
        except ImportError:
            print(
                "Warning: pyyaml is not installed — cannot read config.yaml. "
                "Run: pip install pyyaml --break-system-packages"
            )
        except Exception as e:
            print(f"Warning: could not parse config.yaml ({e}). Using defaults.")
    return _deep_merge({}, _DEFAULTS)


# ── Attribute-access wrapper ───────────────────────────────────────────────────
class _Section:
    """Wraps a config sub-dict with attribute access and a .get() helper."""

    def __init__(self, data: dict) -> None:
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        try:
            return data[name]
        except KeyError:
            raise AttributeError(
                f"Config key '{name}' not found. "
                f"Available keys: {list(data.keys())}"
            ) from None

    def get(self, key: str, default: Any = None) -> Any:
        return object.__getattribute__(self, "_data").get(key, default)

    def __repr__(self) -> str:
        return f"_Section({object.__getattribute__(self, '_data')!r})"


# ── Public config object ───────────────────────────────────────────────────────
class _Config:
    """Top-level config accessor. Access sections as attributes: cfg.vault.base_dir"""

    def __init__(self, data: dict) -> None:
        self._data = data
        self.vault = _Section(data["vault"])
        self.transcription = _Section(data["transcription"])
        self.whisperx = _Section(data["whisperx"])
        self.extraction = _Section(data["extraction"])
        self.graph = _Section(data["graph"])
        self.obsidian = _Section(data["obsidian"])

    def reload(self) -> None:
        """Re-read config.yaml from disk (useful in tests or long-running processes)."""
        data = _load()
        self.__init__(data)


cfg = _Config(_load())
