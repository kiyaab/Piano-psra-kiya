"""
KIYA Piano Studio Pro - Settings Repository
Wrapper around AppConfig for repository-level persistence.
"""

from app.config import AppConfig

class SettingsRepository:
    """Provides repository access to application settings."""

    def __init__(self, config: AppConfig):
        self.config = config

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config.set(key, value)

    def save(self) -> bool:
        return self.config.save()
