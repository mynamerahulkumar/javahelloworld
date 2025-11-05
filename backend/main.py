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

# Configure CORS middleware for Postman access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Postman
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
    
    logger.info(f"Starting Trading API server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

