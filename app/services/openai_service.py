"""Thin OpenAI client wrapper — swap models or providers here later."""

from __future__ import annotations

from typing import Optional, Tuple

from app.config import OPENAI_API_KEY, OPENAI_MODEL

from app.services.api_key_resolution import NO_API_KEY_USER_MESSAGE


def get_openai_api_key() -> Optional[str]:
    return OPENAI_API_KEY


def get_openai_model() -> str:
    # Override via .env OPENAI_MODEL (e.g. gpt-5-mini when your account supports it)
    return OPENAI_MODEL


def is_openai_configured() -> bool:
    """True if the server has OPENAI_API_KEY (env). Does not reflect per-session keys."""
    return get_openai_api_key() is not None


def _effective_key(api_key: Optional[str]) -> Optional[str]:
    raw = (api_key or "").strip()
    if raw:
        return raw
    return OPENAI_API_KEY


def is_generation_configured_with_key(api_key: Optional[str]) -> bool:
    """True if generation can run with this effective key (session override or server)."""
    return _effective_key(api_key) is not None


def _get_client_for_key(api_key: Optional[str]):
    """Return OpenAI client for the given effective key (no global cache when key varies)."""
    from openai import OpenAI

    key = _effective_key(api_key)
    if not key:
        raise RuntimeError("No API key available.")
    return OpenAI(api_key=key, timeout=120.0)


def reset_client_for_tests() -> None:
    """No-op placeholder for older tests that reset a global client."""
    return


def chat_completion_markdown(
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
    api_key: Optional[str] = None,
) -> Tuple[bool, str, str]:
    """
    Single chat completion; expects Markdown in the reply.
    api_key: optional override (e.g. user's session key); falls back to OPENAI_API_KEY.

    Returns (ok, markdown_text, error_message).
    """
    effective = _effective_key(api_key)
    if not effective:
        return False, "", NO_API_KEY_USER_MESSAGE

    try:
        client = _get_client_for_key(api_key)
        model = get_openai_model()
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.35,
            max_tokens=max_tokens,
        )
        choice = resp.choices[0].message
        text = (choice.content or "").strip()
        if not text:
            return False, "", "The model returned empty text."
        return True, text, ""
    except Exception as e:  # noqa: BLE001
        return False, "", f"OpenAI request failed: {e}"
