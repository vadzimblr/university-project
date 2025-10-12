from pydantic import BaseModel
from typing import List, Optional

class Character(BaseModel):
    name: str
    description: str
    first_appeared_scene: Optional[int] = None

class Location(BaseModel):
    name: str
    description: str

class SceneResponse(BaseModel):
    story_uuid: str
    scene_number: int
    characters: List[Character]
    location: Location
    actions: str
    sd_prompt: str
    processing_time: float

class LLMSceneResponse(BaseModel):
    characters: List[Character]
    location: str
    actions: List[str]
    sd_prompt: str
