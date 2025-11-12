import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.push_service import PushNotificationService
from app.models.notification import PushNotificationRequest, NotificationType


@pytest.fixture
def mock_db_session():
    return Mock(spec=AsyncSession)


@pytest.fixture
def push_service(mock_db_session):
    return PushNotificationService(mock_db_session)


@pytest.fixture
def sample_notification_request():
    return PushNotificationRequest(
        notification_type=NotificationType.PUSH,
        user_id="test-user-123",
        template_code="welcome",
        variables={
            "title": "Welcome!",
            "body": "Welcome to our app",
            "data": {"action": "welcome"}
        },
        request_id="req-123",
        priority=1
    )


@pytest.mark.asyncio
async def test_process_notification_success(push_service, sample_notification_request):
    """Test successful notification processing"""
    
    # Mock the push provider
    push_service.push_provider.send_notification = AsyncMock(return_value={
        "success": True,
        "provider": "firebase",
        "message_id": "msg-123"
    })
    
    # Mock database operations
    push_service.db_session.add = Mock()
    push_service.db_session.commit = AsyncMock()
    push_service.db_session.execute = AsyncMock()
    
    result = await push_service.process_notification(
        sample_notification_request,
        "test-device-token",
        "correlation-123"
    )
    
    assert result["success"] is True
    assert "notification_id" in result
    assert result["message"] == "Notification processed successfully"


@pytest.mark.asyncio
async def test_process_notification_failure(push_service, sample_notification_request):
    """Test notification processing failure"""
    
    # Mock the push provider to fail
    push_service.push_provider.send_notification = AsyncMock(return_value={
        "success": False,
        "provider": "firebase",
        "error": "Invalid device token"
    })
    
    # Mock database operations
    push_service.db_session.add = Mock()
    push_service.db_session.commit = AsyncMock()
    push_service.db_session.execute = AsyncMock()
    
    result = await push_service.process_notification(
        sample_notification_request,
        "invalid-token",
        "correlation-123"
    )
    
    assert result["success"] is False
    assert result["error"] == "Invalid device token"


@pytest.mark.asyncio
async def test_get_notification_status(push_service):
    """Test getting notification status"""
    
    # Mock database query result
    mock_notification = Mock()
    mock_notification.id = "notif-123"
    mock_notification.status = "delivered"
    mock_notification.created_at = "2024-01-01T00:00:00Z"
    mock_notification.delivered_at = "2024-01-01T00:01:00Z"
    mock_notification.error_message = None
    
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_notification
    
    push_service.db_session.execute = AsyncMock(return_value=mock_result)
    
    status = await push_service.get_notification_status("notif-123")
    
    assert status is not None
    assert status["notification_id"] == "notif-123"
    assert status["status"] == "delivered"