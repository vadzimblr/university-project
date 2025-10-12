from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Table, UniqueConstraint
from sqlalchemy.orm import relationship

from ...utils.database import Base

scene_characters = Table('scene_characters', Base.metadata,
    Column('scene_id', Integer, ForeignKey('scenes.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('story_characters.id'), primary_key=True)
)

class Scene(Base):
    __tablename__ = "scenes"
    __table_args__ = (
        UniqueConstraint('story_uuid', 'scene_number', name='uq_scenes_story_uuid_scene_number'),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_uuid = Column(String(100), ForeignKey("stories.uuid"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    scene_text = Column(Text, nullable=False)
    location_id = Column(Integer, ForeignKey("story_locations.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    processing_time = Column(Integer, nullable=True)

    story = relationship("Story", back_populates="scenes")
    characters = relationship("StoryCharacter", secondary=scene_characters, back_populates="scenes")
    location = relationship("StoryLocation", back_populates="scenes")
    result = relationship("SceneResult", back_populates="scene", uselist=False)
