#!/usr/bin/env python3
"""
Push Notification Service Startup Script
Handles complete service initialization and startup
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import create_tables, engine
from app.utils.logger import configure_logging
import structlog

# Configure logging
configure_logging(settings.debug)
logger = structlog.get_logger()


async def check_dependencies():
    """Check if all dependencies are available"""
    logger.info("Checking service dependencies...")
    
    # Check database connection
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error("❌ Database connection failed", error=str(e))
        return False
    
    # Check RabbitMQ connection
    try:
        import aio_pika
        connection = await aio_pika.connect_robust(
            settings.rabbitmq_url,
            timeout=5
        )
        await connection.close()
        logger.info("✅ RabbitMQ connection successful")
    except Exception as e:
        logger.error("❌ RabbitMQ connection failed", error=str(e))
        return False
    
    # Check Redis connection
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(settings.redis_url)
        await redis_client.ping()
        await redis_client.close()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error("❌ Redis connection failed", error=str(e))
        return False
    
    return True


async def setup_database():
    """Setup database tables"""
    logger.info("Setting up database tables...")
    try:
        await create_tables()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error("❌ Database setup failed", error=str(e))
        return False
    return True


async def setup_queues():
    """Setup RabbitMQ queues"""
    logger.info("Setting up RabbitMQ queues...")
    try:
        import aio_pika
        connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        channel = await connection.channel()
        
        # Declare push queue
        await channel.declare_queue(settings.push_queue_name, durable=True)
        logger.info(f"✅ Queue '{settings.push_queue_name}' declared")
        
        # Declare failed queue
        await channel.declare_queue(settings.failed_queue_name, durable=True)
        logger.info(f"✅ Queue '{settings.failed_queue_name}' declared")
        
        # Declare status queue
        await channel.declare_queue("notification.status.queue", durable=True)
        logger.info("✅ Queue 'notification.status.queue' declared")
        
        await connection.close()
        return True
    except Exception as e:
        logger.error("❌ Queue setup failed", error=str(e))
        return False


def start_service():
    """Start the FastAPI service"""
    logger.info(f"Starting Push Notification Service on {settings.host}:{settings.port}")
    
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,
        access_log=False
    )


async def main():
    """Main startup function"""
    logger.info("🚀 Starting Push Notification Service")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    logger.info(f"Version: {settings.version}")
    
    # Check dependencies
    if not await check_dependencies():
        logger.error("❌ Dependency check failed. Please ensure all services are running.")
        sys.exit(1)
    
    # Setup database
    if not await setup_database():
        logger.error("❌ Database setup failed")
        sys.exit(1)
    
    # Setup queues
    if not await setup_queues():
        logger.error("❌ Queue setup failed")
        sys.exit(1)
    
    logger.info("✅ All checks passed. Starting service...")
    
    # Start the service
    start_service()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error("Service startup failed", error=str(e))
        sys.exit(1)