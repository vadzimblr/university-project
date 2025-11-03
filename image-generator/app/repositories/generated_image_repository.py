from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.entities.GeneratedImage import GeneratedImage


class GeneratedImageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save_image(
        self,
        story_uuid: str,
        scene_number: int,
        minio_path: str,
        minio_bucket: str,
        file_size: int,
        prompt_id: Optional[str] = None,
        prompt_text: Optional[str] = None
    ) -> GeneratedImage:
        image = GeneratedImage(
            story_uuid=story_uuid,
            scene_number=scene_number,
            minio_path=minio_path,
            minio_bucket=minio_bucket,
            file_size=file_size,
            prompt_id=prompt_id,
            prompt_text=prompt_text
        )
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image
    
    def get_by_story_and_scene(
        self,
        story_uuid: str,
        scene_number: int
    ) -> List[GeneratedImage]:
        return (
            self.db.query(GeneratedImage)
            .filter(
                GeneratedImage.story_uuid == story_uuid,
                GeneratedImage.scene_number == scene_number
            )
            .order_by(GeneratedImage.created_at.desc())
            .all()
        )
    
    def get_latest_by_story_and_scene(
        self,
        story_uuid: str,
        scene_number: int
    ) -> Optional[GeneratedImage]:
        return (
            self.db.query(GeneratedImage)
            .filter(
                GeneratedImage.story_uuid == story_uuid,
                GeneratedImage.scene_number == scene_number
            )
            .order_by(GeneratedImage.created_at.desc())
            .first()
        )
    
    def get_previous_scene_image(
        self,
        story_uuid: str,
        current_scene_number: int
    ) -> Optional[GeneratedImage]:
        return (
            self.db.query(GeneratedImage)
            .filter(
                GeneratedImage.story_uuid == story_uuid,
                GeneratedImage.scene_number < current_scene_number
            )
            .order_by(GeneratedImage.scene_number.desc(), GeneratedImage.created_at.desc())
            .first()
        )
    
    def get_all_by_story(self, story_uuid: str) -> List[GeneratedImage]:
        return (
            self.db.query(GeneratedImage)
            .filter(GeneratedImage.story_uuid == story_uuid)
            .order_by(GeneratedImage.scene_number, GeneratedImage.created_at)
            .all()
        )
    
    def get_all(self, limit: Optional[int] = None) -> List[GeneratedImage]:
        query = (
            self.db.query(GeneratedImage)
            .order_by(GeneratedImage.created_at.desc())
        )
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def delete_by_id(self, image_id: int) -> bool:
        image = self.db.query(GeneratedImage).filter(GeneratedImage.id == image_id).first()
        if not image:
            return False
        
        self.db.delete(image)
        self.db.commit()
        return True

