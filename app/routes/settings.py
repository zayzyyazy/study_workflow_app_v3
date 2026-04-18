"""Per-session OpenAI API key (tester MVP — no accounts)."""

from urllib.parse import quote

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import APP_ROOT
from app.services.api_key_resolution import SESSION_OPENAI_KEY, openai_template_context

templates = Jinja2Templates(directory=str(APP_ROOT / "app" / "templates"))
router = APIRouter()


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    notice = request.query_params.get("notice")
    err = request.query_params.get("error")
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "title": "Settings",
            "notice": notice,
            "error": err,
            **openai_template_context(request),
        },
    )


@router.post("/settings/api-key", response_model=None)
def save_api_key(
    request: Request,
    openai_api_key: str = Form(""),
) -> RedirectResponse:
    key = (openai_api_key or "").strip()
    if not key:
        return RedirectResponse(
            url="/settings?error=" + quote("Paste a non-empty API key, or use Remove."),
            status_code=303,
        )
    request.session[SESSION_OPENAI_KEY] = key
    return RedirectResponse(
        url="/settings?notice=" + quote("Personal API key saved. It overrides the server key for your browser."),
        status_code=303,
    )


@router.post("/settings/api-key/remove", response_model=None)
def remove_api_key(request: Request) -> RedirectResponse:
    request.session.pop(SESSION_OPENAI_KEY, None)
    return RedirectResponse(
        url="/settings?notice=" + quote("Personal API key removed from this browser."),
        status_code=303,
    )
