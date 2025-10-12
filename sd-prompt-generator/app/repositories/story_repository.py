from sqlalchemy.orm import Session

from app.models.entities.Story import Story


class StoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, uuid: str) -> Story:
        story = Story(uuid=uuid)
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        return story

    def get_by_uuid(self, uuid: str) -> type[Story] | None:
        return self.db.query(Story).filter(Story.uuid == uuid).first()
