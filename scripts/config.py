"""config.py - Configuration for the Email Agent skill.

Loads API keys from .env (fully optional) and user preferences
from user_preferences.json (created by setup.py on first run).
All core features work WITHOUT any API key - AI is an enhancement.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


class Config:
    """Environment-based configuration. API keys are fully optional."""

    # ---- AI (optional) ----
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "none").lower()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # ---- Email ----
    EMAIL_IMAP_SERVER: str = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
    EMAIL_SMTP_SERVER: str = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
    EMAIL_ACCOUNT: str = os.getenv("EMAIL_ACCOUNT", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_INBOX_FOLDER: str = os.getenv("EMAIL_INBOX_FOLDER", "INBOX")

    # ---- Operational ----
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
    MAX_EMAILS: int = int(os.getenv("MAX_EMAILS", "10"))
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR", str(ROOT_DIR / "chroma_db")
    )

    @classmethod
    def ai_available(cls) -> bool:
        """Whether any AI backend is configured and usable."""
        return bool(cls.OPENAI_API_KEY) or bool(cls.GEMINI_API_KEY)

    @classmethod
    def ai_label(cls) -> str:
        """Return a human-readable label for the AI mode."""
        if cls.GEMINI_API_KEY:
            return f"Gemini ({cls.GEMINI_MODEL})"
        if cls.OPENAI_API_KEY:
            return f"OpenAI ({cls.OPENAI_MODEL})"
        return "规则引擎（无 API Key）"

    @classmethod
    def validate(cls) -> list[str]:
        """Return warnings (not errors) for missing optional API keys."""
        warnings = []
        if not cls.MOCK_MODE:
            if not cls.EMAIL_ACCOUNT:
                warnings.append("EMAIL_ACCOUNT 未配置，真实模式无法使用")
            if not cls.EMAIL_PASSWORD:
                warnings.append("EMAIL_PASSWORD 未配置，真实模式无法使用")
        return warnings


class UserPreferences:
    """User preferences loaded from user_preferences.json (created by setup.py)."""

    _prefs: dict = {}
    _loaded: bool = False

    @classmethod
    def load(cls) -> dict:
        if cls._loaded:
            return cls._prefs
        prefs_file = ROOT_DIR / "user_preferences.json"
        if prefs_file.exists():
            try:
                cls._prefs = json.load(open(prefs_file, "r", encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                cls._prefs = {}
        cls._loaded = True
        return cls._prefs

    @classmethod
    def get(cls, key: str, default=None):
        cls.load()
        parts = key.split(".")
        val = cls._prefs
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return default
        return val if val is not None else default

    @classmethod
    def is_setup_complete(cls) -> bool:
        return cls.get("setup_complete", False)

    @classmethod
    def get_reply_tone(cls) -> str:
        return cls.get("preferences.reply_tone", "正式")

    @classmethod
    def get_auto_send(cls) -> bool:
        return cls.get("preferences.auto_send", False)

    @classmethod
    def get_daily_summary_enabled(cls) -> bool:
        return cls.get("preferences.daily_summary", True)

    @classmethod
    def get_summary_at_startup(cls) -> bool:
        return cls.get("preferences.summary_at_startup", True)

    @classmethod
    def get_watch_senders(cls) -> list:
        return cls.get("preferences.watch_senders", [])

    @classmethod
    def get_blacklist_senders(cls) -> list:
        return cls.get("preferences.blacklist_senders", [])

    @classmethod
    def get_signature(cls) -> str:
        return cls.get("preferences.signature", "")
