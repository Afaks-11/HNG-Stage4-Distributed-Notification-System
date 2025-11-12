from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import structlog

from app.core.config import settings
from app.core.database import create_tables, close_db
from app.api.push_routes import router as push_router
from app.api.health import router as health_router
from app.services.queue_consumer import QueueConsumer
from app.utils.logger import configure_logging

# Configure logging
configure_logging(settings.debug)
logger = structlog.get_logger()


async def start_consumer_with_retry(consumer, max_retries=5):
    """Start consumer with retry logic"""
    for attempt in range(max_retries):
        try:
            await asyncio.sleep(attempt * 2)  # Wait before retry
            await consumer.start_consuming()
            break
        except Exception as e:
            logger.warning(f"Consumer start attempt {attempt + 1} failed", error=str(e))
            if attempt == max_retries - 1:
                logger.error("Failed to start consumer after all retries")
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    
    # Startup
    logger.info("Starting Push Notification Service", version=settings.version)
    
    # Create database tables
    await create_tables()
    
    # Start queue consumer in background with retry
    consumer = QueueConsumer()
    consumer_task = asyncio.create_task(start_consumer_with_retry(consumer))
    
    yield
    
    # Shutdown
    logger.info("Shutting down Push Notification Service")
    consumer_task.cancel()
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Push Notification Service for distributed notification system",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", "unknown")
    
    # Add to structured logging context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response


# Include routers
app.include_router(health_router)
app.include_router(push_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None  # Use our custom logging
    )