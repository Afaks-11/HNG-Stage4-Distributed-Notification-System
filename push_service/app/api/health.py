from fastapi import APIRouter, status
from typing import Dict, Any
import asyncio
import aio_pika
from sqlalchemy import text
import structlog

from app.core.config import settings
from app.core.database import engine

logger = structlog.get_logger()
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    
    health_status = {
        "service": "push-service",
        "status": "healthy",
        "version": settings.version,
        "checks": {}
    }
    
    # Check database connection
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check RabbitMQ connection
    try:
        connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            timeout=5
        )
        await connection.close()
        health_status["checks"]["rabbitmq"] = "healthy"
    except Exception as e:
        health_status["checks"]["rabbitmq"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check push providers
    health_status["checks"]["onesignal"] = (
        "configured" if settings.onesignal_app_id and settings.onesignal_api_key 
        else "not configured"
    )
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check endpoint"""
    
    return {
        "service": "push-service",
        "ready": True,
        "timestamp": asyncio.get_event_loop().time()
    }