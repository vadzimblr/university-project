from uuid import UUID
from .base import BaseEvent, event


@event
class SceneSavedEvent(BaseEvent):
    def __init__(
        self,
        scene_number: int,
        document_id: UUID,
        scene_text: str,
        scene_id: UUID,
        job_id: UUID,
        word_count: int,
        char_count: int
    ):
        super().__init__()
        self.scene_number = scene_number
        self.document_id = document_id
        self.scene_text = scene_text
        self.scene_id = scene_id
        self.job_id = job_id
        self.word_count = word_count
        self.char_count = char_count
    
    @property
    def event_type(self) -> str:
        return 'scene.saved'
    
    @property
    def exchange_name(self) -> str:
        return 'scene_saved_events'
    
    @property
    def routing_key(self) -> str:
        return 'scene.saved'

    @classmethod
    def get_exchange_name(cls) -> str:
        return 'scene_saved_events'

    @classmethod
    def get_routing_key(cls) -> str:
        return 'scene.saved'

    def to_payload(self):
        return {
            'scene_number': self.scene_number,
            'document_id': self.document_id,
            'scene_text': self.scene_text,
            'scene_id': self.scene_id,
            'job_id': self.job_id,
            'word_count': self.word_count,
            'char_count': self.char_count,
        }
