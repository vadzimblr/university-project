from ...utils.database import Base

from sqlalchemy import Column, String, Integer, ForeignKey, Text, UniqueConstraint

class SceneRepresentation(Base):
    __tablename__ = 'scene_representations'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_uuid = Column(String(100), nullable=False)
    scene_number = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint('story_uuid', 'scene_number', name='uq_story_scene'),
    )
    