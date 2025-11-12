#!/usr/bin/env python3
"""
Push Notification Service Runner
"""
import asyncio
import uvicorn
from app.core.config import settings


def main():
    """Run the push notification service"""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,
        access_log=False
    )


if __name__ == "__main__":
    main()