"""
KIYA Piano Studio Pro - Voice & Instrument Browser
Provides searchable instrument categories, favorites, recent history, and voice previews.
"""

from typing import Dict, List, Tuple, Optional
from app.constants import GM_CATEGORIES

class VoiceBrowser:
    """Manages GM instrument search, category filtering, favorites, and previewing."""

    def __init__(self, favorites: Optional[List[int]] = None, recents: Optional[List[int]] = None):
        self.favorites: List[int] = list(favorites) if favorites else [0, 4, 16, 24, 32, 40, 48, 56]
        self.recents: List[int] = list(recents) if recents else [0, 4, 16, 48]

    def get_categories(self) -> List[str]:
        return list(GM_CATEGORIES.keys())

    def get_voices_in_category(self, category: str) -> List[Tuple[int, str]]:
        return GM_CATEGORIES.get(category, [])

    def search_voices(self, query: str) -> List[Tuple[int, str, str]]:
        """Search voices across all categories. Returns (program, name, category)."""
        q = query.strip().lower()
        results = []
        for cat, voices in GM_CATEGORIES.items():
            for prog, name in voices:
                if not q or q in name.lower() or q in cat.lower():
                    results.append((prog, name, cat))
        return results

    def get_voice_name(self, program: int) -> str:
        for cat, voices in GM_CATEGORIES.items():
            for prog, name in voices:
                if prog == program:
                    return name
        return f"Instrument {program + 1}"

    def get_voice_category(self, program: int) -> str:
        for cat, voices in GM_CATEGORIES.items():
            for prog, name in voices:
                if prog == program:
                    return cat
        return "General"

    def record_usage(self, program: int):
        """Add to recent list."""
        if program in self.recents:
            self.recents.remove(program)
        self.recents.insert(0, program)
        if len(self.recents) > 16:
            self.recents.pop()

    def toggle_favorite(self, program: int) -> bool:
        """Toggle favorite status. Returns True if now favorite."""
        if program in self.favorites:
            self.favorites.remove(program)
            return False
        else:
            self.favorites.append(program)
            return True

    def is_favorite(self, program: int) -> bool:
        return program in self.favorites
