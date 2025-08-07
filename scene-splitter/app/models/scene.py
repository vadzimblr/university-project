from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..utils.database import Base


class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    processing_job_id = Column(UUID(as_uuid=True), ForeignKey("processing_jobs.id"), nullable=False)
    
    scene_number = Column(Integer, nullable=False)
    
    scene_text = Column(Text, nullable=False)
    sentence_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)
    
    start_sentence_idx = Column(Integer)
    end_sentence_idx = Column(Integer)
    
    boundary_confidence = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    
    processing_job = relationship("ProcessingJob", back_populates="scenes")
