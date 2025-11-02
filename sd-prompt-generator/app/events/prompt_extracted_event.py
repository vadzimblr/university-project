from typing import List, Optional
from uuid import UUID
from .base import BaseEvent, event


class PreviousContext:
    def __init__(self, story_uuid: str, scene_number: int, prompt: str):
        self.story_uuid = story_uuid
        self.scene_number = scene_number
        self.prompt = prompt
    
    def to_dict(self):
        return {
            'story_uuid': self.story_uuid,
            'scene_number': self.scene_number,
            'prompt': self.prompt
        }


@event
class PromptExtractedEvent(BaseEvent):
    def __init__(
        self,
        story_uuid: str,
        scene_number: int,
        prompt: str,
        scene_id: UUID,
        previous_contexts: Optional[List[PreviousContext]] = None
    ):
        super().__init__()
        self.story_uuid = story_uuid
        self.scene_number = scene_number
        self.prompt = prompt
        self.scene_id = scene_id
        self.previous_contexts = previous_contexts or []
    
    @property
    def event_type(self) -> str:
        return 'prompt.extracted'
    
    @property
    def exchange_name(self) -> str:
        return 'prompt_extracted_events'
    
    @property
    def routing_key(self) -> str:
        return 'prompt.extracted'

    @classmethod
    def get_exchange_name(cls) -> str:
        return 'prompt_extracted_events'

    @classmethod
    def get_routing_key(cls) -> str:
        return 'prompt.extracted'

    def to_payload(self):
        return {
            'story_uuid': self.story_uuid,
            'scene_number': self.scene_number,
            'prompt': self.prompt,
            'scene_id': self.scene_id,
            'previous_contexts': [ctx.to_dict() for ctx in self.previous_contexts]
        }
