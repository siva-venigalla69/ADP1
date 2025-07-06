"""
Main FastAPI application for Design Gallery backend.
This file configures the FastAPI app and includes all routes.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.designs import router as designs_router
from app.api.admin import router as admin_router
from app.api.upload import router as upload_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Design Gallery API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Design Gallery API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="FastAPI backend for Design Gallery Android App with Cloudflare R2 and D1",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Add middleware
    configure_middleware(app)
    
    # Add exception handlers
    configure_exception_handlers(app)
    
    # Include routers
    configure_routes(app)
    
    # Add basic routes
    add_basic_routes(app)
    
    return app


def configure_middleware(app: FastAPI):
    """Configure application middleware."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Trusted host middleware for production
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure this properly for production
        )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log incoming requests."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
        
        return response


def configure_exception_handlers(app: FastAPI):
    """Configure custom exception handlers."""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail,
                "success": False
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors(),
                "success": False
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "success": False
            }
        )


def configure_routes(app: FastAPI):
    """Configure application routes."""
    
    # API routes
    app.include_router(auth_router, prefix="/api")
    app.include_router(designs_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    app.include_router(upload_router, prefix="/api")


def add_basic_routes(app: FastAPI):
    """Add basic application routes."""
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Design Gallery API",
            "version": settings.app_version,
            "environment": settings.environment,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment
        }
    
    @app.get("/info")
    async def app_info():
        """Application information endpoint."""
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "debug": settings.debug,
            "features": {
                "authentication": True,
                "design_management": True,
                "file_upload": True,
                "admin_panel": True,
                "analytics": True,
                "favorites": True
            }
        }


# Create the FastAPI app
app = create_app()

# Import time for middleware
import time

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    ) 