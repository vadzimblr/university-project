from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..utils.database import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    celery_task_id = Column(String(255), unique=True, index=True)
    
    start_page = Column(Integer, default=1)
    end_page = Column(Integer, default=999)
    
    status = Column(String(50), default="pending", index=True)
    current_step = Column(String(50))
    
    error_message = Column(Text)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    document = relationship("Document", back_populates="processing_jobs")
    scenes = relationship("Scene", back_populates="processing_job")
    
    @property
    def processing_time(self):
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
