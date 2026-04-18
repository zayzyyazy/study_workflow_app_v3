"""FastAPI entry point for Study AI V3 (study_workflow_app_v3)."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from starlette.middleware.sessions import SessionMiddleware

from app.config import APP_ROOT, SESSION_SECRET, ensure_directories
from app.routes import courses, home, lectures, planner, settings as settings_routes, upload
from app.services.database_service import initialize_database

app = FastAPI(
    title="Study AI V3",
    description="Local-first lecture library: study materials, deep dives, planner, and practice questions.",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    max_age=60 * 60 * 24 * 90,
    same_site="lax",
    https_only=False,
)

templates = Jinja2Templates(directory=str(APP_ROOT / "app" / "templates"))


@app.on_event("startup")
def _startup() -> None:
    ensure_directories()
    initialize_database()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> object:
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "title": "Page not found",
                "status_code": 404,
                "message": "That page doesn’t exist or was moved.",
                "hint": "Use the menu to go Home, Planner, Courses, or Upload.",
            },
            status_code=404,
        )
    detail = exc.detail
    if isinstance(detail, str):
        pass
    elif detail is not None:
        detail = str(detail)
    else:
        detail = "Something went wrong."
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "title": "Error",
            "status_code": exc.status_code,
            "message": detail,
            "hint": None,
        },
        status_code=exc.status_code,
    )


# Mount /static after API routes (FastAPI/Starlette convention; avoids routing edge cases).
app.include_router(home.router)
app.include_router(upload.router)
app.include_router(courses.router)
app.include_router(lectures.router)
app.include_router(planner.router)
app.include_router(settings_routes.router)

app.mount(
    "/static",
    StaticFiles(directory=str(APP_ROOT / "app" / "static")),
    name="static",
)
