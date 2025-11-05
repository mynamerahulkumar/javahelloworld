"""
Main FastAPI application entry point
"""
import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Change to backend directory for imports
backend_path = Path(__file__).parent
os.chdir(backend_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as trading_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Trading API",
    description="API for executing trading orders with stop loss and take profit",
    version="1.0.0"
)

# Configure CORS middleware
# In production, use specific origins; in development, allow all for Postman
environment = os.getenv("ENVIRONMENT", "development").lower()
if environment == "production":
    # Production: Use specific origins from environment variable
    allowed_origins = os.getenv("CORS_ORIGINS", "").split(",")
    allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    if not allowed_origins:
        # Default to allow all if not configured (should be configured in production)
        allowed_origins = ["*"]
else:
    # Development: Allow all origins for Postman and local development
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(trading_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Trading API",
        "version": "1.0.0",
        "endpoints": {
            "place_limit_order_wait": "/api/v1/place-limit-order-wait",
            "docs": "/docs"
        }
    }


def main():
    """Main function to run the FastAPI server"""
    import uvicorn
    
    port = int(os.getenv("PORT", 8501))
    host = os.getenv("HOST", "0.0.0.0")
    # Enable reload only in development mode (default: True for local, False for production)
    reload = os.getenv("ENVIRONMENT", "development").lower() != "production"
    workers = int(os.getenv("WORKERS", "1")) if not reload else 1  # Workers only in production
    
    logger.info(f"Starting Trading API server on {host}:{port}")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Reload: {reload}, Workers: {workers if not reload else 1}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )


if __name__ == "__main__":
    main()

