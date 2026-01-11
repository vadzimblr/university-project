from typing import List

from pydantic import BaseModel

from domain.entities import Scene


class SceneResponseDto(BaseModel):
    scene_number: int
    scene_text: str
    sentence_count: int
    word_count: int
    char_count: int

    @classmethod
    def from_entity(cls, entity: Scene) -> "SceneResponseDto":
        return cls(
            scene_number=entity.scene_number,
            scene_text=entity.scene_text,
            sentence_count=entity.sentence_count,
            word_count=entity.word_count,
            char_count=entity.char_count
        )

    @classmethod
    def from_entities(cls, entities: List[Scene]) -> List["SceneResponseDto"]:
        return [cls.from_entity(entity) for entity in entities]
