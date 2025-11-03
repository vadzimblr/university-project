from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(
    title="Image Generator Service",
    description="Generates images from prompts using ComfyUI",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "service": "image-generator",
        "status": "running",
        "description": "Image generation service using inbox pattern"
    }


@app.get("/health")
async def health():
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "image-generator",
            "worker_mode": "inbox-pattern",
            "comfyui_url": os.getenv("COMFYUI_URL", "not configured"),
            "minio_endpoint": os.getenv("MINIO_ENDPOINT", "not configured")
        },
        status_code=200
    )


@app.get("/info")
async def info():
    return {
        "service": "image-generator",
        "components": {
            "api": "FastAPI (health checks only)",
            "worker": "Celery + Inbox Pattern",
            "storage": "MinIO S3",
            "ai_backend": "ComfyUI"
        },
        "endpoints": {
            "health": "/health",
            "info": "/info"
        },
        "note": "This service processes events from inbox table. Use prompt-generator to send image generation requests."
    }

