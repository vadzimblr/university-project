from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProcessingJobStatusResponseDto(BaseModel):
    job_identifier: UUID
    status: str
    current_step: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None

    @classmethod
    def from_entity(cls, job_entity) -> "ProcessingJobStatusResponseDto":
        return cls(
            job_identifier=job_entity.id,
            status=job_entity.status,
            current_step=job_entity.current_step,
            error_message=job_entity.error_message,
            started_at=job_entity.started_at,
            completed_at=job_entity.completed_at,
            processing_time=job_entity.processing_time,
        )
