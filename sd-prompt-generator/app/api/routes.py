from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.schemas.request import SceneRequest
from app.services.llm_service import LLMService
from app.services.context_service import ContextService
import time
import uuid

from app.services.prompt_processing_service import PromptProcessingService

router = APIRouter()

@router.post("/process-scene")
async def process_scene(
    request: SceneRequest,
    prompt_processing_service = Depends(PromptProcessingService)
):
    return prompt_processing_service.process(request)

@router.get("/story/{story_uuid}/context")
async def get_story_context(
    story_uuid: str,
    db: Session = Depends(get_db)
):
    context_service = ContextService(db)
    context = context_service.get_story_context(story_uuid)
    
    return context

@router.get("/story/{story_uuid}/scenes")
async def get_story_scenes(
    story_uuid: str,
    db: Session = Depends(get_db)
):
    scenes = db.query(Scene).filter(Scene.story_uuid == story_uuid).order_by(Scene.scene_number).all()
    
    return [
        {
            "scene_number": scene.scene_number,
            "scene_text": scene.scene_text,
            "processed_at": scene.processed_at,
            "has_result": scene.result is not None
        }
        for scene in scenes
    ]
