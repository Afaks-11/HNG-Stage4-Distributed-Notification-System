from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="Push Notification Service", version="1.0.0")

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "message": "Push Service is healthy",
        "data": {
            "service": "push-service",
            "status": "up",
            "port": 8003
        }
    }

@app.post("/api/v1/push/send")
async def send_push_notification(notification: dict):
    return {
        "success": True,
        "message": "Push notification queued successfully",
        "data": {
            "notification_id": "push-123",
            "status": "queued"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)