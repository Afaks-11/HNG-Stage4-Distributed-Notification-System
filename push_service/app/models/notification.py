from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from enum import Enum
import uuid

Base = declarative_base()

class NotificationStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered" 
    FAILED = "failed"

class NotificationType(str, Enum):
    PUSH = "push"

class PushNotification(Base):
    __tablename__ = "push_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    template_code = Column(String, nullable=False)
    variables = Column(JSON, nullable=True)
    request_id = Column(String, nullable=False, index=True)
    priority = Column(Integer, default=1)
    metadata = Column(JSON, nullable=True)
    
    # Push specific fields
    device_token = Column(String, nullable=False)
    title = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    click_url = Column(String, nullable=True)
    
    # Status tracking
    status = Column(String, default=NotificationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class PushNotificationLog(Base):
    __tablename__ = "push_notification_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)