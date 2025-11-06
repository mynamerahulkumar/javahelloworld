"""
Main FastAPI application entry point
"""
import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Change to backend directory for imports
backend_path = Path(__file__).parent
os.chdir(backend_path)

# Configure logging to write to file AND console
logs_dir = backend_path / "logs"
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / "bot.log"

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove existing handlers to avoid duplicates
root_logger.handlers.clear()

# File handler with rotation (10MB max, keep 5 backups)
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Console handler (for when running directly)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 80)
logger.info("Starting Trading API Server")
logger.info(f"Log file: {log_file}")
logger.info("=" * 80)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from api.routes import router as trading_router
    from api.supabase_routes import router as supabase_router
except Exception as e:
    logger.error(f"Failed to import modules: {e}", exc_info=True)
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Trading API",
    description="API for executing trading orders with stop loss and take profit",
    version="1.0.0"
)

# Add request/error logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests and responses"""
    import time
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error in {request.method} {request.url.path}: {e} - Time: {process_time:.3f}s", exc_info=True)
        raise

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
app.include_router(supabase_router)  # Supabase routes (separate module)

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
    logger.info(f"API Documentation: http://{host}:{port}/docs")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

