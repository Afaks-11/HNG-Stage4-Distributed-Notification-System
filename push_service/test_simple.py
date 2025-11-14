#!/usr/bin/env python3

import asyncio
import json
from app.services.push_service import PushNotificationService
from app.models.notification import PushNotificationRequest
from app.core.database import AsyncSessionLocal

async def test_simple():
    """Simple test without complex logging"""
    
    request_data = {
        "notification_type": "push",
        "user_id": "test-123",
        "template_code": "test",
        "variables": {
            "title": "Test Notification",
            "body": "This is a test"
        },
        "request_id": "test-123",
        "priority": 1
    }
    
    request = PushNotificationRequest(**request_data)
    
    async with AsyncSessionLocal() as session:
        service = PushNotificationService(session)
        result = await service.process_notification(
            request,
            "mock_device_token",
            "test-correlation-id"
        )
        
        print("Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_simple())