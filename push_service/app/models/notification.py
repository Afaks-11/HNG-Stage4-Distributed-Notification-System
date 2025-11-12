from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

Base = declarative_base()


class NotificationStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"


class NotificationType(str, Enum):
    PUSH = "push"


class PushNotification(Base):
    __tablename__ = "push_notifications"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    device_token = Column(String, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    data = Column(Text)  # JSON string
    status = Column(String, default=NotificationStatus.PENDING)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    delivered_at = Column(DateTime(timezone=True))


# Pydantic Models
class PushNotificationRequest(BaseModel):
    notification_type: NotificationType = NotificationType.PUSH
    user_id: str
    template_code: str
    variables: Dict[str, Any]
    request_id: str
    priority: int = Field(default=1, ge=1, le=5)
    metadata: Optional[Dict[str, Any]] = None


class PushNotificationData(BaseModel):
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    click_action: Optional[str] = None


class NotificationStatusUpdate(BaseModel):
    notification_id: str
    status: NotificationStatus
    timestamp: Optional[datetime] = None
    error: Optional[str] = None


class PushNotificationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: str