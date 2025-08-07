from typing import List, Dict, Any
from app.utils.celery import celery_app
from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.utils.database import get_db_session
from sqlalchemy.orm import Session


@celery_app.task(name="save_scenes_task", bind=True)
def save_scenes_task(self, job_id: str, scenes_data: List[Dict[str, Any]]):
    session: Session = get_db_session()
    job_repo = ProcessingJobRepository(session)
    
    try:
        job_repo.update_status(job_id, "splitting", "finalization")
        
        saved_scenes = []
        for scene_data in scenes_data:
            scene = Scene(
                processing_job_id=job_id,
                scene_number=scene_data['scene_number'],
                scene_text=scene_data['scene_text'],
                sentence_count=scene_data['sentence_count'],
                word_count=scene_data['word_count'],
                char_count=scene_data['char_count'],
                start_sentence_idx=scene_data.get('start_sentence_idx'),
                end_sentence_idx=scene_data.get('end_sentence_idx'),
                boundary_confidence=scene_data.get('boundary_confidence')
            )
            session.add(scene)
            saved_scenes.append(scene.scene_number)
        
        session.commit()
        job_repo.update_status(job_id, "completed")
        
        return {
            'status': 'success',
            'saved_scenes_count': len(saved_scenes),
            'scene_numbers': saved_scenes,
            'message': f'Successfully saved {len(saved_scenes)} scenes'
        }
        
    except Exception as e:
        session.rollback()
        job_repo.update_status(job_id, "failed", error_message=str(e))
        
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )
    
    finally:
        session.close() 