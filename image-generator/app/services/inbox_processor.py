import logging
import sys
import asyncio
import os
from typing import Dict, Any

from ..repositories.inbox_repository import InboxRepository
from ..utils.database import get_db_session
from .comfyui_service import ComfyUIService


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
        
        try:
            result = asyncio.run(self._generate_image_async(payload))
            return result
        except Exception as e:
            self.logger.error(f"Failed to generate image: {e}", exc_info=True)
            raise
    
    async def _generate_image_async(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        story_uuid = payload.get('story_uuid')
        scene_number = payload.get('scene_number')
        prompt = payload.get('prompt')
        scene_id = payload.get('scene_id')
        
        session = get_db_session()
        try:
            comfyui_url = os.getenv('COMFYUI_URL', 'http://comfy-ui:8188')
            comfyui_service = ComfyUIService(session, comfyui_url)
            
            reference_image = payload.get('reference_image', '').strip()
            has_reference = bool(reference_image)
            
            if not has_reference:
                from ..utils.image_placeholder import get_placeholder_image
                reference_image = get_placeholder_image()
                ipadapter_weight = 0.0
                ipadapter_start_at = 0.0
                ipadapter_end_at = 0.0
                self.logger.info("No reference image provided, using placeholder and disabling IPAdapter")
            else:
                ipadapter_weight = float(os.getenv('IPADAPTER_WEIGHT', '0.65'))
                ipadapter_start_at = float(os.getenv('IPADAPTER_START_AT', '0.3'))
                ipadapter_end_at = float(os.getenv('IPADAPTER_END_AT', '0.95'))
                self.logger.info("Reference image provided, enabling IPAdapter")
            
            placeholders = {
                'model_name': os.getenv('DEFAULT_MODEL_NAME', 'juggernautXL_ragnarokBy.safetensors'),
                'prompt': prompt,
                'seed': payload.get('seed', self._generate_seed()),
                'steps': int(os.getenv('DEFAULT_STEPS', '20')),
                'cfg': float(os.getenv('DEFAULT_CFG', '8.0')),
                'sampler_name': os.getenv('DEFAULT_SAMPLER', 'euler'),
                'scheduler': os.getenv('DEFAULT_SCHEDULER', 'simple'),
                'width': int(os.getenv('DEFAULT_WIDTH', '512')),
                'height': int(os.getenv('DEFAULT_HEIGHT', '512')),
                'ipadapter_weight': ipadapter_weight,
                'ipadapter_start_at': ipadapter_start_at,
                'ipadapter_end_at': ipadapter_end_at,
                'base64_image': reference_image
            }
            
            self.logger.info(f"Sending generation request to ComfyUI with prompt: {prompt[:100]}...")
            
            generation_result = await comfyui_service.generate_image(
                config_key=payload.get('config_key', 'default'),
                placeholders=placeholders
            )
            
            prompt_id = generation_result['prompt_id']
            self.logger.info(f"Generation started with prompt_id: {prompt_id}")
            
            if os.getenv('WAIT_FOR_COMPLETION', 'true').lower() == 'true':
                self.logger.info(f"Waiting for generation completion...")
                await comfyui_service.wait_for_completion(prompt_id)
                
                images = await comfyui_service.get_generated_images(prompt_id)
                self.logger.info(f"Downloaded {len(images)} images")
                
                # TODO: Сохранить изображения в MinIO/S3
                # TODO: Сохранить ссылки на изображения в БД
                # TODO: Опубликовать событие images.generated
                
                return {
                    'story_uuid': story_uuid,
                    'scene_number': scene_number,
                    'scene_id': scene_id,
                    'prompt_id': prompt_id,
                    'status': 'completed',
                    'images_count': len(images)
                }
            else:
                return {
                    'story_uuid': story_uuid,
                    'scene_number': scene_number,
                    'scene_id': scene_id,
                    'prompt_id': prompt_id,
                    'status': 'queued'
                }
                
        finally:
            session.close()
    
    def _generate_seed(self) -> int:
        import random
        return random.randint(0, 2**32 - 1)
    
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
