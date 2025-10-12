import logging
import sys
from typing import Dict, Any

from app.repositories.inbox_repository import InboxRepository
from app.database.connection import get_db_session
from app.models.schemas.request import SceneRequest
from app.services.prompt_processing_service import PromptProcessingService


class InboxProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.prompt_service = PromptProcessingService()
    
    def process_inbox_events(self, batch_size: int = 10, max_retries: int = 5) -> Dict[str, Any]:
        session = get_db_session()
        inbox_repo = InboxRepository(session)
        
        stats = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'dead_letter': 0,
            'errors': []
        }
        
        try:
            events = inbox_repo.get_unprocessed_events(limit=batch_size, max_retries=max_retries)
            stats['processed'] = len(events)
            
            if not events:
                return stats
            
            self.logger.info(f"Processing {len(events)} events from inbox")
            
            for event in events:
                try:
                    if event.event_type == 'scene.saved':
                        self._process_scene_saved_event(event.payload)
                    else:
                        raise ValueError(f"Unknown event type: {event.event_type}")
                    
                    inbox_repo.mark_as_processed(event.id)
                    stats['succeeded'] += 1
                    
                    self.logger.info(f"Event {event.id} processed successfully")
                    
                except Exception as e:
                    error_msg = str(e)
                    stats['failed'] += 1
                    stats['errors'].append({
                        'event_id': str(event.id),
                        'error': error_msg,
                        'retry_count': event.retry_count + 1
                    })
                    
                    self.logger.error(f"Error processing event {event.id} (attempt {event.retry_count + 1}): {error_msg}")
                    
                    if event.retry_count + 1 >= max_retries:
                        inbox_repo.mark_as_failed(event.id, error_msg)
                        stats['dead_letter'] += 1
                        self.logger.error(f"Event {event.id} moved to DLQ after {max_retries} attempts")
                    else:
                        inbox_repo.increment_retry_count(event.id, error_msg)
            
            return stats
            
        finally:
            session.close()
    
    def _process_scene_saved_event(self, payload: Dict[str, Any]):
        scene_number = payload['scene_number']
        document_id = payload['document_id']
        scene_text = payload['scene_text']
        
        self.logger.info(f"Processing scene #{scene_number} from document {document_id}")
        
        scene_request = SceneRequest(
            story_uuid=document_id,
            scene_number=scene_number,
            scene_text=scene_text
        )
        
        result = self.prompt_service.process(scene_request)
        
        self.logger.info(f"SD prompt generated: {result.sd_prompt[:100]}...")
        
        return result
    
    def cleanup_old_events(self, older_than_days: int = 7) -> int:
        session = get_db_session()
        inbox_repo = InboxRepository(session)
        
        try:
            deleted = inbox_repo.delete_processed_events(older_than_days)
            if deleted > 0:
                self.logger.info(f"Deleted old events: {deleted}")
            return deleted
        finally:
            session.close()
