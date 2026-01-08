from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.database import engine, Base
from app.api.endpoints import auth, loans, covenants, alerts, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="CovenantIQ - AI-powered loan covenant monitoring platform for European markets",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(covenants.router)
app.include_router(alerts.router)
app.include_router(analytics.router)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for Railway deployment"""
    return {
        "status": "healthy",
        "service": "covenantiq-api",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "CovenantIQ API - AI-Powered Loan Covenant Monitoring",
        "version": "1.0.0",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
