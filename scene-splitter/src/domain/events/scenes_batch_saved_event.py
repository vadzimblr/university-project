from typing import List
from uuid import UUID
from .base import BaseEvent, event


@event
class ScenesBatchSavedEvent(BaseEvent):
    EVENT_TYPE = "scenes.batch_saved"

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

    def to_payload(self):
        return {
            'job_id': self.job_id,
            'document_id': self.document_id,
            'scene_ids': self.scene_ids,
            'total_count': self.total_count,
        }
