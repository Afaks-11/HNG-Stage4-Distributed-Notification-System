from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
import structlog
from app.models.notification import PushNotificationData
from app.core.config import settings

logger = structlog.get_logger()


class PushProvider(ABC):
    """Abstract base class for push notification providers"""
    
    @abstractmethod
    async def send_notification(
        self,
        device_token: str,
        notification_data: PushNotificationData,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        pass


class MockPushProvider(PushProvider):
    """Mock push provider for testing"""
    
    async def send_notification(
        self,
        device_token: str,
        notification_data: PushNotificationData,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        
        logger.info(
            "Mock notification sent",
            correlation_id=correlation_id,
            device_token=device_token,
            title=notification_data.title
        )
        
        return {
            "success": True,
            "provider": "mock",
            "message_id": f"mock_{correlation_id}"
        }


class OneSignalPushProvider(PushProvider):
    """OneSignal push notification provider"""
    
    def __init__(self):
        self.app_id = settings.onesignal_app_id
        self.api_key = settings.onesignal_api_key
        self.base_url = "https://onesignal.com/api/v1"
    
    async def send_notification(
        self,
        device_token: str,
        notification_data: PushNotificationData,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        if not self.app_id or not self.api_key:
            return {
                "success": False,
                "provider": "onesignal",
                "error": "OneSignal credentials not configured"
            }
        
        try:
            headers = {
                "Authorization": f"Basic {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "app_id": self.app_id,
                "include_player_ids": [device_token],
                "headings": {"en": notification_data.title},
                "contents": {"en": notification_data.body},
                "data": notification_data.data or {},
            }
            
            if notification_data.image_url:
                payload["big_picture"] = notification_data.image_url
            
            if notification_data.click_action:
                payload["url"] = notification_data.click_action
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/notifications",
                    json=payload,
                    headers=headers
                )
                
                result = response.json()
                
                if response.status_code == 200 and result.get("id"):
                    logger.info(
                        "OneSignal notification sent",
                        correlation_id=correlation_id,
                        notification_id=result["id"]
                    )
                    return {
                        "success": True,
                        "provider": "onesignal",
                        "message_id": result["id"]
                    }
                else:
                    logger.error(
                        "OneSignal notification failed",
                        correlation_id=correlation_id,
                        response=result
                    )
                    return {
                        "success": False,
                        "provider": "onesignal",
                        "error": result.get("errors", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(
                "OneSignal notification failed",
                correlation_id=correlation_id,
                error=str(e)
            )
            return {
                "success": False,
                "provider": "onesignal",
                "error": str(e)
            }


class PushProviderFactory:
    """Factory for creating push providers"""
    
    @staticmethod
    def create_provider(provider_type: str = "mock") -> PushProvider:
        if provider_type == "onesignal":
            return OneSignalPushProvider()
        else:
            return MockPushProvider()