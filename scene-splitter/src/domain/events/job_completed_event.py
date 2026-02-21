from uuid import UUID
from .base import BaseEvent, event


@event
class JobCompletedEvent(BaseEvent):
    EVENT_TYPE = "job.completed"

    def __init__(
        self,
        job_id: UUID,
        document_id: UUID,
        total_scenes: int
    ):
        super().__init__()
        self.job_id = job_id
        self.document_id = document_id
        self.total_scenes = total_scenes

    def to_payload(self):
        return {
            'job_id': self.job_id,
            'document_id': self.document_id,
            'total_scenes': self.total_scenes,
        }
