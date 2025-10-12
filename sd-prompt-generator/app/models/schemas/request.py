from pydantic import BaseModel

class SceneRequest(BaseModel):
    story_uuid: str
    scene_number: int
    scene_text: str
