from pydantic import BaseModel


class SceneStatisticDto(BaseModel):
    scene_number: int
    sentence_count: int
    word_count: int
    char_count: int
