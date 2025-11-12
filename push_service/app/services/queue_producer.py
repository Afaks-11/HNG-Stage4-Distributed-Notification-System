import json
import uuid
from typing import Dict, Any, Optional
import aio_pika
from aio_pika import Message
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class QueueProducer:
    """RabbitMQ producer for sending messages to other services"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            logger.info("Producer connected to RabbitMQ")
        except Exception as e:
            logger.error("Failed to connect producer to RabbitMQ", error=str(e))
            raise
    
    async def send_status_update(
        self,
        notification_id: str,
        status: str,
        error: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Send notification status update to status queue"""
        
        if not self.channel:
            await self.connect()
        
        try:
            # Declare status queue
            status_queue = await self.channel.declare_queue(
                "notification.status.queue",
                durable=True
            )
            
            status_data = {
                "notification_id": notification_id,
                "status": status,
                "service": "push-service",
                "timestamp": str(uuid.uuid4()),  # Use proper timestamp in production
                "error": error
            }
            
            message = Message(
                json.dumps(status_data).encode(),
                correlation_id=correlation_id or str(uuid.uuid4())
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key="notification.status.queue"
            )
            
            logger.info(
                "Status update sent",
                notification_id=notification_id,
                status=status,
                correlation_id=correlation_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to send status update",
                notification_id=notification_id,
                error=str(e)
            )
    
    async def send_to_failed_queue(
        self,
        original_message: Dict[str, Any],
        error: str,
        correlation_id: Optional[str] = None
    ):
        """Send failed message to dead letter queue"""
        
        if not self.channel:
            await self.connect()
        
        try:
            failed_queue = await self.channel.declare_queue(
                settings.failed_queue_name,
                durable=True
            )
            
            failed_data = {
                "original_message": original_message,
                "error": error,
                "service": "push-service",
                "failed_at": str(uuid.uuid4()),  # Use proper timestamp
                "correlation_id": correlation_id
            }
            
            message = Message(
                json.dumps(failed_data).encode(),
                correlation_id=correlation_id or str(uuid.uuid4())
            )
            
            await self.channel.default_exchange.publish(
                message,
                routing_key=settings.failed_queue_name
            )
            
            logger.info(
                "Message sent to failed queue",
                correlation_id=correlation_id,
                error=error
            )
            
        except Exception as e:
            logger.error(
                "Failed to send to failed queue",
                error=str(e)
            )
    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Producer connection closed")