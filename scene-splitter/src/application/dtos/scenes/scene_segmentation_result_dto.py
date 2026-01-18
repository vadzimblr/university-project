from pydantic import BaseModel


class SceneSegmentationResultDto(BaseModel):
    scenes_count: int
    text_length: int
