from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid

from ..models.processing_job import ProcessingJob
from ..models.enums import ProcessingStatus, ProcessingStep


class ProcessingJobRepository:

    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self, 
        document_id: uuid.UUID, 
        celery_task_id: str,
        start_page: int = 1,
        end_page: int = 999
    ) -> ProcessingJob:
        job = ProcessingJob(
            document_id=document_id,
            celery_task_id=celery_task_id,
            start_page=start_page,
            end_page=end_page
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_by_id(self, job_id: uuid.UUID) -> Optional[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    
    def get_by_celery_task_id(self, celery_task_id: str) -> Optional[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.celery_task_id == celery_task_id
        ).first()
    
    def get_by_document_id(self, document_id: uuid.UUID) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.document_id == document_id
        ).order_by(desc(ProcessingJob.created_at)).all()
    
    def get_by_status(self, status: ProcessingStatus) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.status == status
        ).order_by(desc(ProcessingJob.created_at)).all()
    
    def get_active_jobs(self) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.status.notin_([ProcessingStatus.COMPLETED, ProcessingStatus.FAILED])
        ).order_by(desc(ProcessingJob.created_at)).all()
    
    def update_status(
        self,
        job: ProcessingJob,
        status: ProcessingStatus,
        step: Optional[ProcessingStep] = None,
        progress: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> ProcessingJob:
        job.status = status
        
        if step:
            job.current_step = step
        if progress is not None:
            job.progress_percentage = progress
        if error_message:
            job.error_message = error_message
            
        if status == ProcessingStatus.EXTRACTING and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
            job.completed_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def start_processing(self, job: ProcessingJob) -> ProcessingJob:
        return self.update_status(
            job, 
            ProcessingStatus.EXTRACTING, 
            ProcessingStep.TEXT_EXTRACTION,
            progress=0
        )
    
    def complete_processing(self, job: ProcessingJob) -> ProcessingJob:
        return self.update_status(
            job,
            ProcessingStatus.COMPLETED,
            ProcessingStep.FINALIZATION,
            progress=100
        )
    
    def fail_processing(self, job: ProcessingJob, error_message: str) -> ProcessingJob:
        return self.update_status(
            job,
            ProcessingStatus.FAILED,
            error_message=error_message
        )
    
    def update(self, job: ProcessingJob) -> ProcessingJob:
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def delete(self, job_id: uuid.UUID) -> bool:
        job = self.get_by_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False
