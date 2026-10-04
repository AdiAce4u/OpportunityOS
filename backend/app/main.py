import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import init_db, SessionLocal
from app.db.seed import seed_database
from app.api.routes import api_router
from app.services.mock_portal import portal_router

app = FastAPI(
    title="OpportunityOS API",
    description="Autonomous Agentic Job Discovery, Resume Tailoring, Browser Automation & Tracking Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("screenshots", exist_ok=True)

# Mount static files for resume downloads and screenshots
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

# Register routers
app.include_router(api_router)
app.include_router(portal_router)

@app.on_event("startup")
def startup_event():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
