from uuid import UUID

from pydantic import BaseModel


class ProcessingJobCreatedResponseDto(BaseModel):
    job_identifier: UUID
    task_identifier: str
    document_identifier: UUID
    status: str
    message: str

    @classmethod
    def from_values(
        cls,
        job_identifier: UUID,
        task_identifier: str,
        document_identifier: UUID
    ) -> "ProcessingJobCreatedResponseDto":
        return cls(
            job_identifier=job_identifier,
            task_identifier=task_identifier,
            document_identifier=document_identifier,
            status="pending",
            message="Processing started"
        )
