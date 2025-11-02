import logging
import sys
from typing import Dict, Any

from ..repositories.inbox_repository import InboxRepository
from ..utils.database import get_db_session


class InboxProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
    
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
                    if event.event_type == 'prompt.extracted':
                        self._process_prompt_extracted_event(event.payload)
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
    
    def _process_prompt_extracted_event(self, payload: Dict[str, Any]):
        story_uuid = payload.get('story_uuid')
        scene_number = payload.get('scene_number')
        prompt = payload.get('prompt')
        scene_id = payload.get('scene_id')
        previous_contexts = payload.get('previous_contexts', [])
        
        self.logger.info(f"Processing prompt.extracted event for story {story_uuid}, scene #{scene_number}")
        self.logger.info(f"Prompt: {prompt}")
        self.logger.info(f"Scene ID: {scene_id}")
        
        if previous_contexts:
            self.logger.info(f"Previous contexts: {len(previous_contexts)} scenes")
        
        # TODO: Implement actual image generation logic here
        # This is where you would:
        # 1. Load the image generation configuration
        # 2. Call the ComfyUI service or SD API
        # 3. Save the generated images to storage
        # 4. Update the database with image URLs/paths
        # 5. Publish an event that images were generated
        
        self.logger.info(f"Image generation for scene #{scene_number} completed (TODO: implement actual generation)")
        
        return {
            'story_uuid': story_uuid,
            'scene_number': scene_number,
            'scene_id': scene_id,
            'status': 'pending_implementation'
        }
    
    def cleanup_old_events(self, older_than_days: int = 7) -> int:
        session = get_db_session()
        inbox_repo = InboxRepository(session)
        
        try:
            deleted = inbox_repo.delete_processed_events(older_than_days)
            if deleted > 0:
                self.logger.info(f"Deleted {deleted} old processed events")
            return deleted
        finally:
            session.close()
