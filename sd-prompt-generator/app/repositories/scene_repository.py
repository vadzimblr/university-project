import logging
import sys
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.entities.Scene import Scene
from app.models.schemas.request import SceneRequest


class SceneRepository:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def create_from_request(self, request_data: SceneRequest) -> Scene:
        scene = Scene(
            story_uuid=request_data.story_uuid,
            scene_number=request_data.scene_number,
            scene_text=request_data.scene_text,
        )
        self.db.add(scene)
        self.db.commit()
        self.db.refresh(scene)
        return scene

    def get_by_story_uuid_and_scene_number(self, story_uuid: str, scene_number: int) -> Optional[Scene]:
        self.logger.info(f"SceneRepository session id: {id(self.db)}")
        return self.db.query(Scene).filter(
            Scene.story_uuid == story_uuid,
            Scene.scene_number == scene_number
        ).first()

    def get_by_id(self, scene_id: int) -> type[Scene] | None:
        return self.db.query(Scene).filter(Scene.id == scene_id).first()

    def get_by_story_uuid(self, story_uuid: str) -> list[type[Scene]]:
        return self.db.query(Scene).filter(Scene.story_uuid == story_uuid).all()

    def set_scene_location(self, location_id: int, scene_id: int) -> type[Scene] | None:
        scene = self.get_by_id(scene_id)
        if scene:
            scene.location_id = location_id
            self.db.commit()
            self.db.refresh(scene)
        return scene

    def update_processing_result(self, scene_id: int, processing_time: float) -> type[Scene] | None:
        scene = self.get_by_id(scene_id)
        if scene:
            scene.processing_time = processing_time
            scene.processed_at = datetime.now()
            self.db.commit()
            self.db.refresh(scene)
        return scene

    def delete(self, scene_id: int) -> bool:
        scene = self.get_by_id(scene_id)
        if scene:
            self.db.delete(scene)
            self.db.commit()
            return True
        return False