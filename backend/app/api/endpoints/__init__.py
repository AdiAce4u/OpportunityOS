from app.api.endpoints.profiles import router as profiles_router
from app.api.endpoints.jobs import router as jobs_router
from app.api.endpoints.applications import router as applications_router
from app.api.endpoints.agent import router as agent_router
from app.api.endpoints.tracker import router as tracker_router

__all__ = [
    "profiles_router",
    "jobs_router",
    "applications_router",
    "agent_router",
    "tracker_router",
]
