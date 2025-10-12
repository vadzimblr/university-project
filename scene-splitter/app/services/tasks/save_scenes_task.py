from typing import List, Dict, Any
from uuid import UUID
from app.utils.celery import celery_app
from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.outbox_repository import OutboxRepository
from app.utils.database import get_db_session
from app.events import SceneSavedEvent, ScenesBatchSavedEvent, JobCompletedEvent
from sqlalchemy.orm import Session


@celery_app.task(name="save_scenes_task", bind=True)
def save_scenes_task(self, job_id: str, scenes_data: List[Dict[str, Any]]):
    session: Session = get_db_session()
    job_repo = ProcessingJobRepository(session)
    outbox_repo = OutboxRepository(session)
    
    try:
        job_repo.update_status(job_id, "splitting", "finalization")
        
        job = job_repo.get_by_id(job_id)
        if not job:
            raise ValueError(f"Processing job {job_id} not found")
        
        document_id = job.document_id
        saved_scenes = []
        scene_ids = []
        
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
            session.flush()
            
            scene_saved_event = SceneSavedEvent(
                scene_number=scene.scene_number,
                document_id=document_id,
                scene_text=scene.scene_text,
                scene_id=scene.id,
                job_id=UUID(job_id),
                word_count=scene.word_count,
                char_count=scene.char_count
            )

            outbox_repo.create_event(
                event=scene_saved_event,
                session=session
            )
            
            saved_scenes.append(scene.scene_number)
            scene_ids.append(scene.id)
        
        batch_saved_event = ScenesBatchSavedEvent(
            job_id=UUID(job_id),
            document_id=document_id,
            scene_ids=scene_ids,
            total_count=len(saved_scenes)
        )
        outbox_repo.create_event(event=batch_saved_event, session=session)
        
        job_completed_event = JobCompletedEvent(
            job_id=UUID(job_id),
            document_id=document_id,
            total_scenes=len(saved_scenes)
        )
        outbox_repo.create_event(event=job_completed_event, session=session)
        
        session.commit()
        job_repo.update_status(job_id, "completed")
        
        return {
            'status': 'success',
            'saved_scenes_count': len(saved_scenes),
            'scene_numbers': saved_scenes,
            'message': f'Successfully saved {len(saved_scenes)} scenes and events'
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