from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from ...utils.database import Base


class StoryLocation(Base):
    __tablename__ = "story_locations"

    id = Column(Integer, primary_key=True, index=True)
    story_uuid = Column(String(255), ForeignKey("stories.uuid"), nullable=False)
    name = Column(String(255), nullable=False, default="")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    story = relationship("Story", back_populates="locations")
    scenes = relationship("Scene", back_populates="location")
