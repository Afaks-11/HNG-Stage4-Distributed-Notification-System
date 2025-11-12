import httpx
import redis.asyncio as redis
from typing import Optional, Dict, Any
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class UserServiceClient:
    """Client for communicating with User Service"""
    
    def __init__(self):
        self.user_service_url = settings.user_service_url
        self.redis_client = None
        self.cache_ttl = 300  # 5 minutes cache
    
    async def _get_redis_client(self):
        """Get Redis client for caching"""
        if not self.redis_client:
            self.redis_client = redis.from_url(settings.redis_url)
        return self.redis_client
    
    async def get_user_device_token(self, user_id: str) -> Optional[str]:
        """Get user device token with caching"""
        
        # Try cache first
        cache_key = f"user_device_token:{user_id}"
        redis_client = await self._get_redis_client()
        
        try:
            cached_token = await redis_client.get(cache_key)
            if cached_token:
                logger.info("Device token found in cache", user_id=user_id)
                return cached_token.decode()
        except Exception as e:
            logger.warning("Redis cache error", error=str(e))
        
        # Fetch from User Service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}/device-token",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    device_token = data.get("data", {}).get("push_token")
                    
                    if device_token:
                        # Cache the token
                        try:
                            await redis_client.setex(
                                cache_key,
                                self.cache_ttl,
                                device_token
                            )
                        except Exception as e:
                            logger.warning("Failed to cache device token", error=str(e))
                        
                        logger.info("Device token fetched from User Service", user_id=user_id)
                        return device_token
                    else:
                        logger.warning("No device token found for user", user_id=user_id)
                        return None
                else:
                    logger.error(
                        "Failed to fetch device token",
                        user_id=user_id,
                        status_code=response.status_code
                    )
                    return None
                    
        except httpx.TimeoutException:
            logger.error("User Service timeout", user_id=user_id)
            return None
        except Exception as e:
            logger.error("User Service error", user_id=user_id, error=str(e))
            return None
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        
        cache_key = f"user_preferences:{user_id}"
        redis_client = await self._get_redis_client()
        
        try:
            cached_prefs = await redis_client.get(cache_key)
            if cached_prefs:
                import json
                return json.loads(cached_prefs.decode())
        except Exception as e:
            logger.warning("Redis cache error for preferences", error=str(e))
        
        # Fetch from User Service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.user_service_url}/api/v1/users/{user_id}/preferences",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    preferences = data.get("data", {})
                    
                    # Cache preferences
                    try:
                        import json
                        await redis_client.setex(
                            cache_key,
                            self.cache_ttl,
                            json.dumps(preferences)
                        )
                    except Exception as e:
                        logger.warning("Failed to cache preferences", error=str(e))
                    
                    return preferences
                else:
                    logger.error(
                        "Failed to fetch user preferences",
                        user_id=user_id,
                        status_code=response.status_code
                    )
                    return {"push": True}  # Default preference
                    
        except Exception as e:
            logger.error("User Service error for preferences", user_id=user_id, error=str(e))
            return {"push": True}  # Default preference
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()