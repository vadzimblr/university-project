from pydantic import BaseModel

class PreviousContext(BaseModel):
    story_uuid: str
    scene_number: int
    prompt: str
