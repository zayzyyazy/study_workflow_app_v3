"""Resolve which OpenAI API key to use for the current browser session (tester MVP)."""

from __future__ import annotations

from typing import Literal

from starlette.requests import Request

from app.config import OPENAI_API_KEY

SESSION_OPENAI_KEY = "user_openai_api_key"

Source = Literal["personal", "server", "none"]


def resolve_effective_openai_key(request: Request) -> tuple[str | None, Source]:
    """
    Priority: personal key in signed session → server OPENAI_API_KEY → none.

    Returns (effective_key_or_none, source_label).
    """
    personal = ""
    try:
        raw = request.session.get(SESSION_OPENAI_KEY)
        if isinstance(raw, str):
            personal = raw.strip()
    except (AttributeError, TypeError):
        personal = ""

    if personal:
        return personal, "personal"

    if OPENAI_API_KEY:
        return OPENAI_API_KEY, "server"

    return None, "none"


NO_API_KEY_USER_MESSAGE = (
    "No API key available. Add your OpenAI key in Settings, or ask the host to set OPENAI_API_KEY on the server."
)


def openai_template_context(request: Request) -> dict[str, object]:
    """Pass into TemplateResponse context for status banners."""
    key, source = resolve_effective_openai_key(request)
    return {
        "openai_key_status": source,
        "openai_generation_ready": key is not None,
    }
