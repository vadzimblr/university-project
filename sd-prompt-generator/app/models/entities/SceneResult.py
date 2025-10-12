from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship


from ...utils.database import Base


class SceneResult(Base):
    __tablename__ = "scene_results"

    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False)

    characters_data = Column(JSON)
    location_data = Column(JSON)
    actions = Column(Text)
    sd_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    scene = relationship("Scene", back_populates="result")