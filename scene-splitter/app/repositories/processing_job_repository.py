from typing import Optional, List, Union
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid
from enum import Enum

from ..models.processing_job import ProcessingJob
from ..models.enums import ProcessingStatus, ProcessingStep


class ProcessingJobRepository:

    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self, 
        document_id: str, 
        start_page: int = 1,
        end_page: int = 999,
        celery_task_id: Optional[str] = None
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
    
    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    
    def get_by_celery_task_id(self, celery_task_id: str) -> Optional[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.celery_task_id == celery_task_id
        ).first()
    
    def update_status(
        self,
        job_id: str,
        status: Union[str, ProcessingStatus],
        step: Optional[Union[str, ProcessingStep]] = None,
        error_message: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if not job:
            return None

        if isinstance(status, Enum):
            status_str = status.value
        else:
            status_str = str(status)
        job.status = status_str

        if step:
            step_str = step.value if isinstance(step, Enum) else str(step)
            job.current_step = step_str
        if error_message:
            job.error_message = error_message

        if status_str == ProcessingStatus.EXTRACTING.value and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status_str in [ProcessingStatus.COMPLETED.value, ProcessingStatus.FAILED.value]:
            job.completed_at = datetime.utcnow()
            
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def update_celery_task_id(self, job_id: str, celery_task_id: str) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if not job:
            return None
            
        job.celery_task_id = celery_task_id
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def start_processing(self, job_id: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            ProcessingStatus.EXTRACTING,
            ProcessingStep.TEXT_EXTRACTION
        )

    def complete_processing(self, job_id: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            ProcessingStatus.COMPLETED,
            ProcessingStep.FINALIZATION
        )
    
    def fail_processing(self, job_id: str, error_message: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            ProcessingStatus.FAILED,
            error_message=error_message
        )
    
    def update(self, job: ProcessingJob) -> ProcessingJob:
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def delete(self, job_id: str) -> bool:
        job = self.get_by_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False
