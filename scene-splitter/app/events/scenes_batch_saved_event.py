from typing import List
from uuid import UUID
from .base import BaseEvent, event


@event
class ScenesBatchSavedEvent(BaseEvent):
    def __init__(
        self,
        job_id: UUID,
        document_id: UUID,
        scene_ids: List[UUID],
        total_count: int
    ):
        super().__init__()
        self.job_id = job_id
        self.document_id = document_id
        self.scene_ids = scene_ids
        self.total_count = total_count
    
    @property
    def event_type(self) -> str:
        return 'scenes.batch_saved'

    @property
    def exchange_name(self) -> str:
        return 'scenes_batch_saved_events'

    @property
    def routing_key(self) -> str:
        return 'scenes.batch_saved'

    @classmethod
    def get_exchange_name(cls) -> str:
        return 'scene_saved_events'

    @classmethod
    def get_routing_key(cls) -> str:
        return 'job.completed'

    def to_payload(self):
        return {
            'job_id': self.job_id,
            'document_id': self.document_id,
            'scene_ids': self.scene_ids,
            'total_count': self.total_count,
        }
