from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import os
from sqlalchemy.orm import Session

from .utils.database import get_db
from .repositories.generated_image_repository import GeneratedImageRepository
from .services.minio_service import MinioService

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


@app.get("/stories/{story_uuid}/scenes/{scene_number}/image")
async def get_latest_scene_image(
    story_uuid: str,
    scene_number: int,
    expires_seconds: int = Query(3600, ge=60, le=86400),
    db: Session = Depends(get_db)
):
    image_repo = GeneratedImageRepository(db)
    image = image_repo.get_latest_by_story_and_scene(story_uuid, scene_number)

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    minio_service = MinioService(
        endpoint=os.getenv('MINIO_ENDPOINT', 'minio:9000'),
        access_key=os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
        secret_key=os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
        secure=os.getenv('MINIO_SECURE', 'false').lower() == 'true'
    )

    image_url = minio_service.get_presigned_public_url(
        bucket_name=image.minio_bucket,
        object_name=image.minio_path,
        expires_seconds=expires_seconds
    )

    return {
        "story_uuid": image.story_uuid,
        "scene_number": image.scene_number,
        "image": {
            "id": image.id,
            "bucket": image.minio_bucket,
            "object_name": image.minio_path,
            "size": image.file_size,
            "created_at": image.created_at.isoformat() if image.created_at else None,
            "prompt_id": image.prompt_id,
            "prompt_text": image.prompt_text,
            "url": image_url,
            "expires_in": expires_seconds,
        }
    }
