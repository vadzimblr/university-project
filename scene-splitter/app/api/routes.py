from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.services.tasks.extract_text_task import extract_text_task
from app.models import Document, ProcessingJob, Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.document_repository import DocumentRepository
from app.utils.database import get_db

router = APIRouter()


@router.post("/split-scenes/")
async def split_scenes_from_pdf(
    file: UploadFile = File(...),
    start_page: int = Form(1),
    end_page: int = Form(999),
    session: Session = Depends(get_db)
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    pdf_bytes = await file.read()
    
    doc_repo = DocumentRepository(session)
    document = doc_repo.create(
        filename=file.filename,
        file_size=len(pdf_bytes),
        mime_type=file.content_type or "application/pdf"
    )
    
    job_repo = ProcessingJobRepository(session)
    job = job_repo.create(
        document_id=str(document.id),
        start_page=start_page,
        end_page=end_page
    )
    
    task = extract_text_task.delay(str(job.id), pdf_bytes, start_page, end_page)
    job_repo.update_celery_task_id(str(job.id), task.id)
    
    return {
        "job_id": str(job.id),
        "task_id": task.id,
        "document_id": str(document.id),
        "status": "pending",
        "message": "Processing started"
    }


@router.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: str,
    session: Session = Depends(get_db)
):
    job_repo = ProcessingJobRepository(session)
    job = job_repo.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job_id,
        "status": job.status,
        "current_step": job.current_step,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "processing_time": job.processing_time
    }


@router.get("/jobs/{job_id}/scenes")
async def get_job_scenes(
    job_id: str,
    session: Session = Depends(get_db)
):
    job_repo = ProcessingJobRepository(session)
    job = job_repo.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed yet")
    
    scenes = session.query(Scene).filter(
        Scene.processing_job_id == job_id
    ).order_by(Scene.scene_number).all()
    
    return {
        "job_id": job_id,
        "scenes_count": len(scenes),
        "scenes": [
            {
                "scene_number": scene.scene_number,
                "scene_text": scene.scene_text,
                "sentence_count": scene.sentence_count,
                "word_count": scene.word_count,
                "char_count": scene.char_count,
                "boundary_confidence": scene.boundary_confidence
            }
            for scene in scenes
        ]
    }
