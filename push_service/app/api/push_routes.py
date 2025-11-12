from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import structlog

from app.core.database import AsyncSessionLocal
from app.services.push_service import PushNotificationService
from app.models.notification import (
    PushNotificationRequest,
    PushNotificationResponse,
    NotificationStatusUpdate
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/push", tags=["push"])


def get_db():
    session = AsyncSessionLocal()
    try:
        return session
    finally:
        pass


@router.post("/send", response_model=PushNotificationResponse)
async def send_push_notification(
    request: PushNotificationRequest
):
    """Send a push notification directly (for testing)"""
    
    async with AsyncSessionLocal() as session:
        try:
            push_service = PushNotificationService(session)
            
            # Mock device token for testing
            device_token = f"mock_device_token_{request.user_id}"
            
            result = await push_service.process_notification(
                request,
                device_token,
                request.request_id
            )
            
            return PushNotificationResponse(
                success=result["success"],
                data={"notification_id": result["notification_id"]},
                message=result["message"],
                error=result.get("error")
            )
            
        except Exception as e:
            logger.error("Push notification send failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


@router.get("/status/{notification_id}")
async def get_notification_status(
    notification_id: str,
    db_session: AsyncSession = Depends(get_db)
):
    """Get notification status"""
    
    try:
        push_service = PushNotificationService(db_session)
        status_info = await push_service.get_notification_status(notification_id)
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {
            "success": True,
            "data": status_info,
            "message": "Status retrieved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Status retrieval failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/status")
async def update_notification_status(
    status_update: NotificationStatusUpdate,
    db_session: AsyncSession = Depends(get_db)
):
    """Update notification status (webhook endpoint)"""
    
    try:
        push_service = PushNotificationService(db_session)
        
        await push_service._update_notification_status(
            status_update.notification_id,
            status_update.status,
            status_update.error
        )
        
        return {
            "success": True,
            "message": "Status updated successfully"
        }
        
    except Exception as e:
        logger.error("Status update failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )