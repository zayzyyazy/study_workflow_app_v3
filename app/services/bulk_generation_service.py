"""Run generation for all lectures in a course that are ready_for_generation."""

from __future__ import annotations

from typing import Any

from app.services import lecture_service, openai_service
from app.services.lecture_generation import run_study_materials_generation


def run_bulk_generate_ready_in_course(course_id: int, api_key: str | None = None) -> dict[str, Any]:
    """
    Synchronously generate study materials for each lecture with status ready_for_generation.
    Returns counts: succeeded, failed, skipped (lectures not in ready state), ready (attempted).
    If API key missing, returns ok=False with error message.

    api_key: per-session override from Settings; falls back to server OPENAI_API_KEY.
    """
    if not openai_service.is_generation_configured_with_key(api_key):
        from app.services.api_key_resolution import NO_API_KEY_USER_MESSAGE

        return {
            "ok": False,
            "error": NO_API_KEY_USER_MESSAGE,
        }

    all_lecs = lecture_service.list_lectures_for_course(course_id)
    ready = [l for l in all_lecs if l.get("status") == "ready_for_generation"]
    skipped = len(all_lecs) - len(ready)

    succeeded = 0
    failed = 0
    for lec in ready:
        ok, _msg = run_study_materials_generation(int(lec["id"]), api_key=api_key)
        if ok:
            succeeded += 1
        else:
            failed += 1

    return {
        "ok": True,
        "succeeded": succeeded,
        "failed": failed,
        "skipped": skipped,
        "ready": len(ready),
    }
