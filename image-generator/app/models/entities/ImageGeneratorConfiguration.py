from ...utils.database import Base

from sqlalchemy import Column, String, Integer, Text

class ImageGeneratorConfiguration(Base):
    __tablename__ = 'image_generator_configurations'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(100), unique=True, nullable=False)
    configuration = Column(Text, nullable=False)
