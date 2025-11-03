from typing import Optional
from sqlalchemy.orm import Session
from uuid import uuid4

from ..models.entities.ImageGeneratorConfiguration import ImageGeneratorConfiguration


class ConfigurationRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save_configuration(self, key: str, configuration_json: str) -> ImageGeneratorConfiguration:
        config = ImageGeneratorConfiguration(
            uuid=str(uuid4()),
            key=key,
            configuration=configuration_json
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config
    
    def get_configuration_by_key(self, key: str) -> Optional[ImageGeneratorConfiguration]:
        return (
            self.db.query(ImageGeneratorConfiguration)
            .filter(ImageGeneratorConfiguration.key == key)
            .first()
        )
    
    def get_configuration_by_uuid(self, uuid: str) -> Optional[ImageGeneratorConfiguration]:
        return (
            self.db.query(ImageGeneratorConfiguration)
            .filter(ImageGeneratorConfiguration.uuid == uuid)
            .first()
        )
    
    def get_default_configuration(self) -> Optional[ImageGeneratorConfiguration]:
        return self.get_configuration_by_key('default')
    
    def update_configuration(self, key: str, configuration_json: str) -> bool:
        config = self.get_configuration_by_key(key)
        if not config:
            return False
        
        config.configuration = configuration_json
        self.db.commit()
        return True
    
    def update_configuration_by_uuid(self, uuid: str, configuration_json: str) -> bool:
        config = self.get_configuration_by_uuid(uuid)
        if not config:
            return False
        
        config.configuration = configuration_json
        self.db.commit()
        return True
    
    def delete_configuration(self, key: str) -> bool:
        config = self.get_configuration_by_key(key)
        if not config:
            return False
        
        self.db.delete(config)
        self.db.commit()
        return True
