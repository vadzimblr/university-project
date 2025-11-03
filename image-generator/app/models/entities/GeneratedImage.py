from ...utils.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, Index
from datetime import datetime


class GeneratedImage(Base):
    __tablename__ = 'generated_images'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    story_uuid = Column(String(100), nullable=False, index=True)
    scene_number = Column(Integer, nullable=False, index=True)
    
    minio_path = Column(String(500), nullable=False)
    minio_bucket = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    prompt_id = Column(String(100), nullable=True)
    prompt_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_story_scene', 'story_uuid', 'scene_number'),
    )

