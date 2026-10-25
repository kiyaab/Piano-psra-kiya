"""
KIYA Piano Studio Pro - Project Repository (.kiya file format)
Saves and loads complete musical projects, session state, registrations, and notes.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

class ProjectRepository:
    """Manages reading and writing KIYA project bundle files (.kiya)."""

    PROJECT_EXTENSION = ".kiya"

    @classmethod
    def save_project(cls, file_path: str, project_data: Dict[str, Any]) -> bool:
        """Save project state to .kiya JSON file safely."""
        path = Path(file_path)
        if path.suffix.lower() != cls.PROJECT_EXTENSION:
            path = path.with_suffix(cls.PROJECT_EXTENSION)

        tmp_path = path.with_suffix(".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, indent=2)
            if path.exists():
                path.unlink()
            tmp_path.rename(path)
            print(f"[ProjectRepository] Saved project: {path}")
            return True
        except Exception as e:
            print(f"[ProjectRepository] Error saving project: {e}")
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            return False

    @classmethod
    def load_project(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """Load project state from .kiya JSON file."""
        path = Path(file_path)
        if not path.exists():
            print(f"[ProjectRepository] Project file not found: {file_path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"[ProjectRepository] Error loading project: {e}")
            return None
