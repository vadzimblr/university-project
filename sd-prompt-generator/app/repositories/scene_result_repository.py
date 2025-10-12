from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

from app.models.entities.SceneResult import SceneResult
from app.models.schemas.response import LLMSceneResponse, SceneResponse


class SceneResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, scene_id: int, characters_data: List[dict[str, Any]], location_data: dict,
               actions: str, sd_prompt: str) -> SceneResult:
        scene_result = SceneResult(
            scene_id=scene_id,
            characters_data=characters_data,
            location_data=location_data,
            actions=actions,
            sd_prompt=sd_prompt,
            created_at=datetime.now()
        )
        self.db.add(scene_result)
        self.db.commit()
        self.db.refresh(scene_result)
        return scene_result

    def get_by_id(self, result_id: int) -> Optional[SceneResult]:
        return self.db.query(SceneResult).filter(SceneResult.id == result_id).first()


    def get_by_story_uuid(self, story_uuid: UUID) -> list[type[SceneResult]]:
        return (self.db.query(SceneResult)
                .join(SceneResult.scene)
                .filter(SceneResult.scene.has(story_uuid=story_uuid))
                .order_by(SceneResult.scene_id)
                .all())

    def get_by_scene_id(self, scene_id: int) -> Optional[SceneResult]:
        return self.db.query(SceneResult).filter(SceneResult.scene_id == scene_id).first()

    def get_latest_by_story(self, story_uuid: UUID) -> Optional[SceneResult]:
        return (self.db.query(SceneResult)
                .join(SceneResult.scene)
                .filter(SceneResult.scene.has(story_uuid=story_uuid))
                .order_by(desc(SceneResult.created_at))
                .first())

    def create_from_llm_response(self, scene_id: int, llm_response: LLMSceneResponse) -> SceneResult:
        return self.create(
            scene_id=scene_id,
            characters_data=[char.model_dump() for char in llm_response.characters],
            location_data={"name": llm_response.location, "description": ""},
            actions=", ".join(llm_response.actions),
            sd_prompt=llm_response.sd_prompt
        )

    def to_pydantic(self, scene_result: SceneResult) -> SceneResponse:
        from app.models.schemas.response import Character, Location

        return SceneResponse(
            story_uuid=scene_result.scene.story_uuid,
            scene_number=scene_result.scene.scene_number,
            characters=[Character(**char) for char in scene_result.characters_data],
            location=Location(**scene_result.location_data),
            actions=scene_result.actions,
            sd_prompt=scene_result.sd_prompt,
            processing_time=(datetime.now() - scene_result.created_at).total_seconds()
        )

    def exists_for_scene(self, scene_id: int) -> bool:
        return self.db.query(SceneResult.id).filter(SceneResult.scene_id == scene_id).first() is not None

    def get_scene_count_by_story(self, story_uuid: UUID) -> int:
        return (self.db.query(SceneResult)
                .join(SceneResult.scene)
                .filter(SceneResult.scene.has(story_uuid=story_uuid))
                .count())
