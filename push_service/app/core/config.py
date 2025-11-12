from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App Settings
    app_name: str = "Push Notification Service"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8003
    
    # RabbitMQ Settings
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    push_queue_name: str = "push.queue"
    failed_queue_name: str = "failed.queue"
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # Push Provider Settings
    push_provider: str = "onesignal"
    
    # OneSignal Settings
    onesignal_app_id: Optional[str] = None
    onesignal_api_key: Optional[str] = None
    
    # Database Settings
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/push_service"
    
    # Service URLs
    user_service_url: str = "http://localhost:8001"
    template_service_url: str = "http://localhost:8002"
    
    # Retry Settings
    max_retries: int = 3
    retry_delay: int = 5
    circuit_breaker_threshold: int = 5
    
    # Monitoring
    metrics_port: int = 8004
    
    # Security
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    api_key: str = "your-api-key-for-service-communication"
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()