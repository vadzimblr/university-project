from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from .Scene import scene_characters
from ...utils.database import Base


class StoryCharacter(Base):
    __tablename__ = "story_characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_uuid = Column(String(100), ForeignKey("stories.uuid"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    first_appeared_scene = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    story = relationship("Story", back_populates="characters")
    scenes = relationship("Scene", secondary=scene_characters, back_populates="characters")