from typing import List, Dict, Any
from app.utils.celery import celery_app
from app.services.scene_splitter import SceneSplitterService
from app.models import ProcessingJob, Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.utils.database import get_db_session
from sqlalchemy.orm import Session


@celery_app.task(name="scene_splitting_task", bind=True)
def scene_splitting_task(self, job_id: str, extracted_text: str):
    session: Session = get_db_session()
    job_repo = ProcessingJobRepository(session)
    
    try:
        job_repo.update_status(job_id, "splitting", "scene_splitting")
        
        splitter = SceneSplitterService()
        scenes, valleys, smoothed = splitter.analyze_scenes(extracted_text)
        scene_stats = splitter.get_scene_statistics(scenes)
        
        scenes_data = []
        for i, (scene_text, stats) in enumerate(zip(scenes, scene_stats)):
            scenes_data.append({
                'scene_number': i + 1,
                'scene_text': scene_text,
                'sentence_count': stats['sentence_count'],
                'word_count': stats['word_count'],
                'char_count': stats['char_count'],
                'start_sentence_idx': None,
                'end_sentence_idx': None,
                'boundary_confidence': None
            })
        
        from app.services.tasks.save_scenes_task import save_scenes_task
        save_scenes_task.delay(job_id, scenes_data)
        
        return {
            'status': 'success',
            'scenes_count': len(scenes),
            'valleys_found': len(valleys),
            'message': f'Found {len(scenes)} scenes in text'
        }
        
    except Exception as e:
        job_repo.update_status(job_id, "failed", error_message=str(e))
        
        raise self.retry(
            exc=e,
            countdown=60 * (2 ** self.request.retries),
            max_retries=3
        )
    
    finally:
        session.close() 