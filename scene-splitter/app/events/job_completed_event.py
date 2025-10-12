from uuid import UUID
from .base import BaseEvent, event


@event
class JobCompletedEvent(BaseEvent):
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
    
    @property
    def event_type(self) -> str:
        return 'job.completed'
    
    @property
    def exchange_name(self) -> str:
        return 'job_completed_events'
    
    @property
    def routing_key(self) -> str:
        return 'job.completed'

    @classmethod
    def get_exchange_name(cls) -> str:
        return 'job_completed_events'

    @classmethod
    def get_routing_key(cls) -> str:
        return 'job.completed'

    def to_payload(self):
        return {
            'job_id': self.job_id,
            'document_id': self.document_id,
            'total_scenes': self.total_scenes,
        }
