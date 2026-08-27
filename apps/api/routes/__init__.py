"""FastAPI router aggregators."""
from apps.api.routes.projects import router as projects_router
from apps.api.routes.generation import router as generation_router
from apps.api.routes.jobs import router as jobs_router
from apps.api.routes.assets import router as assets_router

__all__ = [
    "projects_router",
    "generation_router",
    "jobs_router",
    "assets_router"
]
