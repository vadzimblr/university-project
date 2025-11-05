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
    
    def get_all(self, limit: int = 100) -> list[Story]:
        return self.db.query(Story).order_by(Story.created_at.desc()).limit(limit).all()