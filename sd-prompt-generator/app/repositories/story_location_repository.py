from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.entities.StoryLocation import StoryLocation
from app.models.schemas.internal import Location


class StoryLocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_from_location_dto(self, location_dto: Location, story_uuid: str) -> StoryLocation:
        story_location = StoryLocation(
            story_uuid = story_uuid,
            name = "",
            description = location_dto.description,
        )
        self.db.add(story_location)
        self.db.commit()
        self.db.refresh(story_location)

        return story_location

    def get_by_location_id(self, location_id: int) -> Optional[StoryLocation]:
        return self.db.query(StoryLocation).filter(StoryLocation.id == location_id).first()
