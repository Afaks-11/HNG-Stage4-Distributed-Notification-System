import json
import asyncio
from typing import Dict, Any
import aio_pika
from aio_pika import Message, IncomingMessage
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.push_service import PushNotificationService
from app.services.queue_producer import QueueProducer
from app.services.user_service_client import UserServiceClient
from app.models.notification import PushNotificationRequest
from app.core.database import AsyncSessionLocal

logger = structlog.get_logger()


class QueueConsumer:
    """RabbitMQ consumer for push notifications"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.push_queue = None
        self.failed_queue = None
        self.producer = QueueProducer()
        self.user_client = UserServiceClient()
    
    async def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(settings.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Declare queues
            self.push_queue = await self.channel.declare_queue(
                settings.push_queue_name,
                durable=True
            )
            
            self.failed_queue = await self.channel.declare_queue(
                settings.failed_queue_name,
                durable=True
            )
            
            logger.info("Connected to RabbitMQ", queue=settings.push_queue_name)
            
        except Exception as e:
            logger.error("Failed to connect to RabbitMQ", error=str(e))
            raise
    
    async def start_consuming(self):
        """Start consuming messages from the push queue"""
        if not self.push_queue:
            await self.connect()
        
        await self.push_queue.consume(self._process_message)
        logger.info("Started consuming push notifications")
        
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            await self.close()
    
    async def _process_message(self, message: IncomingMessage):
        """Process incoming push notification message"""
        correlation_id = message.correlation_id or "unknown"
        
        try:
            # Parse message body
            message_data = json.loads(message.body.decode())
            
            logger.info(
                "Processing push notification",
                correlation_id=correlation_id,
                user_id=message_data.get("user_id")
            )
            
            # Validate message format
            notification_request = PushNotificationRequest(**message_data)
            
            # Get user device token from User Service
            device_token = await self.user_client.get_user_device_token(
                notification_request.user_id
            )
            
            # Check user preferences
            preferences = await self.user_client.get_user_preferences(
                notification_request.user_id
            )
            
            if not preferences.get("push", True):
                logger.info(
                    "User has disabled push notifications",
                    correlation_id=correlation_id,
                    user_id=notification_request.user_id
                )
                await message.ack()
                return
            
            if not device_token:
                logger.warning(
                    "No device token found for user",
                    correlation_id=correlation_id,
                    user_id=notification_request.user_id
                )
                await self.producer.send_to_failed_queue(
                    message_data,
                    "No device token found",
                    correlation_id
                )
                await message.ack()
                return
            
            # Process notification
            async with AsyncSessionLocal() as db_session:
                push_service = PushNotificationService(db_session)
                result = await push_service.process_notification(
                    notification_request,
                    device_token,
                    correlation_id
                )
            
            if result["success"]:
                logger.info(
                    "Push notification processed successfully",
                    correlation_id=correlation_id,
                    notification_id=result["notification_id"]
                )
                await message.ack()
            else:
                logger.error(
                    "Push notification processing failed",
                    correlation_id=correlation_id,
                    error=result.get("error")
                )
                await self.producer.send_to_failed_queue(
                    message_data,
                    result.get("error"),
                    correlation_id
                )
                await message.ack()
                
        except Exception as e:
            logger.error(
                "Error processing push notification message",
                correlation_id=correlation_id,
                error=str(e)
            )
            await self.producer.send_to_failed_queue(
                json.loads(message.body.decode()) if message.body else {},
                str(e),
                correlation_id
            )
            await message.ack()
    

    

    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.user_client:
            await self.user_client.close()
        if self.producer:
            await self.producer.close()
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed")