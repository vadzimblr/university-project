from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship

from ...utils.database import Base


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    scenes = relationship("Scene", back_populates="story")
    characters = relationship("StoryCharacter", back_populates="story")
    locations = relationship("StoryLocation", back_populates="story")
