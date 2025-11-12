import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from tenacity import retry, stop_after_attempt, wait_exponential
import structlog

from app.models.notification import (
    PushNotification, 
    NotificationStatus, 
    PushNotificationData,
    PushNotificationRequest
)
from app.services.push_provider import PushProviderFactory, PushProvider
from app.services.queue_producer import QueueProducer
from app.utils.circuit_breaker import CircuitBreaker
from app.utils.logger import log_notification_event
from app.core.config import settings

logger = structlog.get_logger()


class PushNotificationService:
    """Service for handling push notifications"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.push_provider: PushProvider = PushProviderFactory.create_provider()
        self.queue_producer = QueueProducer()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_threshold
        )
    
    async def process_notification(
        self,
        notification_request: PushNotificationRequest,
        device_token: str,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """Process a push notification request"""
        
        notification_id = str(uuid.uuid4())
        
        try:
            # Create notification record
            notification = await self._create_notification_record(
                notification_id,
                notification_request,
                device_token
            )
            
            log_notification_event(
                logger,
                "notification_created",
                notification_id,
                correlation_id,
                user_id=notification_request.user_id
            )
            
            # Process notification data
            notification_data = await self._prepare_notification_data(
                notification_request
            )
            
            # Send notification with circuit breaker
            result = await self.circuit_breaker.call(
                self._send_with_retry,
                device_token,
                notification_data,
                correlation_id
            )
            
            # Update notification status
            status = NotificationStatus.DELIVERED if result["success"] else NotificationStatus.FAILED
            await self._update_notification_status(
                notification_id,
                status,
                result.get("error")
            )
            
            # Send status update to other services
            await self.queue_producer.send_status_update(
                notification_id,
                status.value,
                result.get("error"),
                correlation_id
            )
            
            log_notification_event(
                logger,
                "notification_processed",
                notification_id,
                correlation_id,
                success=result["success"]
            )
            
            return {
                "notification_id": notification_id,
                "success": result["success"],
                "message": "Notification processed successfully" if result["success"] else "Notification failed",
                "error": result.get("error")
            }
            
        except Exception as e:
            logger.error(
                "Notification processing failed",
                notification_id=notification_id,
                correlation_id=correlation_id,
                error=str(e)
            )
            
            await self._update_notification_status(
                notification_id,
                NotificationStatus.FAILED,
                str(e)
            )
            
            return {
                "notification_id": notification_id,
                "success": False,
                "message": "Notification processing failed",
                "error": str(e)
            }
    
    async def _create_notification_record(
        self,
        notification_id: str,
        request: PushNotificationRequest,
        device_token: str
    ) -> PushNotification:
        """Create notification record in database"""
        
        notification = PushNotification(
            id=notification_id,
            user_id=request.user_id,
            device_token=device_token,
            title=request.variables.get("title", "Notification"),
            body=request.variables.get("body", "You have a new notification"),
            data=json.dumps(request.variables.get("data", {})),
            status=NotificationStatus.PENDING
        )
        
        self.db_session.add(notification)
        await self.db_session.commit()
        
        return notification
    
    async def _prepare_notification_data(
        self,
        request: PushNotificationRequest
    ) -> PushNotificationData:
        """Prepare notification data from request"""
        
        return PushNotificationData(
            title=request.variables.get("title", "Notification"),
            body=request.variables.get("body", "You have a new notification"),
            data=request.variables.get("data", {}),
            image_url=request.variables.get("image_url"),
            click_action=request.variables.get("click_action")
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _send_with_retry(
        self,
        device_token: str,
        notification_data: PushNotificationData,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """Send notification with retry logic"""
        
        return await self.push_provider.send_notification(
            device_token,
            notification_data,
            correlation_id
        )
    
    async def _update_notification_status(
        self,
        notification_id: str,
        status: NotificationStatus,
        error_message: Optional[str] = None
    ):
        """Update notification status in database"""
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == NotificationStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        
        if error_message:
            update_data["error_message"] = error_message
        
        await self.db_session.execute(
            update(PushNotification)
            .where(PushNotification.id == notification_id)
            .values(**update_data)
        )
        await self.db_session.commit()
    
    async def get_notification_status(self, notification_id: str) -> Optional[Dict[str, Any]]:
        """Get notification status"""
        
        result = await self.db_session.execute(
            select(PushNotification).where(PushNotification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        
        if not notification:
            return None
        
        return {
            "notification_id": notification.id,
            "status": notification.status,
            "created_at": notification.created_at,
            "delivered_at": notification.delivered_at,
            "error_message": notification.error_message
        }