"""
AI-Based MTC Verification System — FastAPI Backend
Main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, SessionLocal
from auth.router import router as auth_router
from documents.router import router as documents_router
from validation.standards import seed_standards

# Create all database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="MTC Verification System",
    description="AI-powered Material Test Certificate verification",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(documents_router)


@app.on_event("startup")
def on_startup():
    """Seed the database with material standards on first startup."""
    db = SessionLocal()
    try:
        seed_standards(db)
    finally:
        db.close()


@app.get("/")
def root():
    """Redirect to documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "MTC Verification System"}


@app.get("/api/standards")
def list_standards():
    """List all available material standards."""
    from models import MaterialStandard
    db = SessionLocal()
    try:
        standards = db.query(MaterialStandard).all()
        return [
            {
                "id": s.id,
                "standard_name": s.standard_name,
                "grade": s.grade,
            }
            for s in standards
        ]
    finally:
        db.close()
