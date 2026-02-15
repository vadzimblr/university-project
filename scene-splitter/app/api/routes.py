from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session

from app.services.tasks.extract_text_task import extract_text_task
from app.models import Scene, Document
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.document_repository import DocumentRepository
from app.models.enums import ProcessingStatus
from app.utils.database import get_db
from app.services.job_approval_service import (
    JobApprovalService,
    JobNotFoundError,
    JobAlreadyApprovedError,
    JobNotReadyError,
    ScenesMissingError,
)
from app.services.scene_update_service import (
    SceneUpdateService,
    JobNotEditableError,
    SceneNotFoundError,
)
from app.services.scene_query_service import (
    SceneQueryService,
    SceneNotFoundError as SceneQueryNotFound,
    JobNotFoundError as JobQueryNotFound,
)
from app.api.schemas import (
    ScenePatchRequest,
    ScenePatchResponse,
    SceneResponse,
    DocumentsResponse,
    DocumentItem,
    ProcessingJobRef,
    SceneSentencesResponse,
    SceneSentence,
)

router = APIRouter()

@router.get("/documents", response_model=DocumentsResponse)
async def list_documents(session: Session = Depends(get_db)):
    documents = session.query(Document).all()
    return DocumentsResponse(
        documents=[
            DocumentItem(
                id=doc.id,
                filename=doc.filename,
                file_size=doc.file_size,
                mime_type=doc.mime_type,
                created_at=doc.created_at.isoformat() if doc.created_at else None,
                processing_jobs=[
                    ProcessingJobRef(
                        id=job.id,
                        status=str(job.status),
                        current_step=str(job.current_step) if job.current_step else None,
                    )
                    for job in doc.processing_jobs
                ],
            )
            for doc in documents
        ]
    )


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
    
    def _normalize_status(raw):
        if hasattr(raw, "value"):
            return raw.value
        if isinstance(raw, str) and raw.startswith("ProcessingStatus."):
            name = raw.split(".", 1)[1]
            if name in ProcessingStatus.__members__:
                return ProcessingStatus[name].value
        return raw

    def _normalize_step(raw):
        return raw.value if hasattr(raw, "value") else raw
    
    return {
        "job_id": job_id,
        "status": _normalize_status(job.status),
        "current_step": _normalize_step(job.current_step),
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
    
    def _normalize_status_value(raw):
        if hasattr(raw, "value"):
            return raw.value
        if isinstance(raw, str) and raw.startswith("ProcessingStatus."):
            name = raw.split(".", 1)[1]
            if name in ProcessingStatus.__members__:
                return ProcessingStatus[name].value
        return raw

    status_value = _normalize_status_value(job.status)
    allowed_statuses = {
        ProcessingStatus.COMPLETED.value,
        ProcessingStatus.APPROVED.value,
        ProcessingStatus.READY_FOR_REVIEW.value,
        "completed",
        "approved",
        "ready-for-review",
    }
    if status_value not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Scenes are not ready yet")
    
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

@router.get("/jobs/{job_id}/scenes/{scene_number}/sentences", response_model=SceneSentencesResponse)
async def get_scene_sentences(
    job_id: str,
    scene_number: int,
    session: Session = Depends(get_db)
):
    service = SceneQueryService(session)
    try:
        sentences = service.get_scene_sentences(job_id, scene_number)
    except JobQueryNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SceneQueryNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

    return SceneSentencesResponse(
        job_id=job_id,
        scene_number=scene_number,
        sentences=[
            SceneSentence(index=i + 1, text=sent)
            for i, sent in enumerate(sentences)
        ],
    )


@router.patch("/jobs/{job_id}/scenes", response_model=ScenePatchResponse)
async def patch_job_scenes(
    job_id: str,
    payload: ScenePatchRequest,
    session: Session = Depends(get_db)
):
    service = SceneUpdateService(session)

    try:
        updated_scenes = service.update_scenes(job_id, [scene.model_dump() for scene in payload.scenes])
    except JobNotEditableError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SceneNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ScenePatchResponse(
        job_id=job_id,
        scenes=[
            SceneResponse(
                scene_id=scene.id,
                scene_number=scene.scene_number,
                scene_text=scene.scene_text,
                sentence_count=scene.sentence_count,
                word_count=scene.word_count,
                char_count=scene.char_count,
                start_sentence_idx=scene.start_sentence_idx,
                end_sentence_idx=scene.end_sentence_idx,
                boundary_confidence=scene.boundary_confidence,
            )
            for scene in updated_scenes
        ]
    )

@router.post("/jobs/{job_id}/approve")
async def approve_job(
    job_id: str,
    session: Session = Depends(get_db)
):
    service = JobApprovalService(session)
    try:
        result = service.approve(job_id)
        return {
            **result,
            "message": "Scenes approved and events queued"
        }
    except JobNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except JobAlreadyApprovedError as e:
        return {"job_id": job_id, "status": ProcessingStatus.APPROVED, "message": str(e)}
    except JobNotReadyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ScenesMissingError as e:
        raise HTTPException(status_code=400, detail=str(e))
