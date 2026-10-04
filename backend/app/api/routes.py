from fastapi import APIRouter
from app.api.endpoints.profiles import router as profiles_router
from app.api.endpoints.jobs import router as jobs_router
from app.api.endpoints.applications import router as applications_router
from app.api.endpoints.agent import router as agent_router
from app.api.endpoints.tracker import router as tracker_router

api_router = APIRouter(prefix="/api")

@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "OpportunityOS API",
        "version": "1.0.0",
        "features": {
            "autonomous_search": True,
            "truth_preserving_tailoring": True,
            "browser_agent": True,
            "human_in_the_loop": True
        }
    }

api_router.include_router(profiles_router)
api_router.include_router(jobs_router)
api_router.include_router(applications_router)
api_router.include_router(agent_router)
api_router.include_router(tracker_router)
