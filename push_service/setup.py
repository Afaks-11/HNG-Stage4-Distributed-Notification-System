#!/usr/bin/env python3
"""
Setup script for Push Notification Service
"""
import asyncio
import os
from app.core.database import create_tables
from app.core.config import settings


async def setup_database():
    """Setup database tables"""
    print("Setting up database tables...")
    try:
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")


def setup_environment():
    """Setup environment file"""
    env_file = ".env"
    env_example = ".env.example"
    
    if not os.path.exists(env_file) and os.path.exists(env_example):
        print("Creating .env file from template...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print("✅ .env file created. Please update with your configuration.")
    else:
        print("ℹ️  .env file already exists or template not found")


async def main():
    """Run setup"""
    print("🚀 Setting up Push Notification Service\n")
    
    setup_environment()
    print()
    await setup_database()
    
    print(f"\n✨ Setup completed!")
    print(f"Service will run on: http://{settings.host}:{settings.port}")
    print(f"Health check: http://{settings.host}:{settings.port}/health")


if __name__ == "__main__":
    asyncio.run(main())