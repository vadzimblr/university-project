from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities import Scene


class SceneRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_scenes_by_processing_job_identifier(self, job_identifier: UUID) -> list[type[Scene]]:
        scenes = self.db_session.query(Scene).filter(
            Scene.processing_job_id == job_identifier
        ).order_by(Scene.scene_number).all()

        return scenes

    def add(self, scene: Scene, commit: bool = True) -> Scene:
        self.db_session.add(scene)

        if commit:
            self.db_session.commit()
            self.db_session.refresh(scene)
        else:
            self.db_session.flush()

        return scene
