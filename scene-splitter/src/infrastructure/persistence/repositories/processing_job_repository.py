from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

from domain.entities.processing_job import ProcessingJob


class ProcessingJobRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

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
        self.db_session.add(job)
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        return self.db_session.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()

    def get_by_celery_task_id(self, celery_task_id: str) -> Optional[ProcessingJob]:
        return self.db_session.query(ProcessingJob).filter(
            ProcessingJob.celery_task_id == celery_task_id
        ).first()

    def update_status(
            self,
            job_id: str,
            status: str,
            step: Optional[str] = None,
            error_message: Optional[str] = None
    ) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if not job:
            return None

        job.status = status

        if step:
            job.current_step = step
        if error_message:
            job.error_message = error_message

        if status == "extracting" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()

        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def update_celery_task_id(self, job_id: str, celery_task_id: str) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if not job:
            return None

        job.celery_task_id = celery_task_id
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def start_processing(self, job_id: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            "extracting",
            "text_extraction"
        )

    def complete_processing(self, job_id: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            "completed",
            "finalization"
        )

    def fail_processing(self, job_id: str, error_message: str) -> Optional[ProcessingJob]:
        return self.update_status(
            job_id,
            "failed",
            error_message=error_message
        )

    def update(self, job: ProcessingJob) -> ProcessingJob:
        self.db_session.commit()
        self.db_session.refresh(job)
        return job

    def delete(self, job_id: str) -> bool:
        job = self.get_by_id(job_id)
        if job:
            self.db_session.delete(job)
            self.db_session.commit()
            return True
        return False
