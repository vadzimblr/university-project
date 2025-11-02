import logging
from kombu import Connection, Queue, Exchange, Consumer
from typing import Dict, Any
from ..utils.celery import get_broker_url
from ..utils.database import get_db_session
from ..repositories.inbox_repository import InboxRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptExtractedConsumer:
    def __init__(self, broker_url: str):
        self.broker_url = broker_url
        self.exchange = Exchange('prompt_extracted_events', type='topic', durable=True)
        self.queue = Queue(
            'image_generator_prompt_queue',
            exchange=self.exchange,
            routing_key='prompt.extracted',
            durable=True
        )
    
    def handle_message(self, body: Dict[str, Any], message):
        session = None
        try:
            event_type = body.get('event_type')
            timestamp = body.get('timestamp')
            payload = body.get('payload', {})
            
            logger.info(f"Received event: {event_type} at {timestamp}")
            logger.info(f"Story UUID: {payload.get('story_uuid')}")
            logger.info(f"Scene number: {payload.get('scene_number')}")
            logger.info(f"Prompt: {payload.get('prompt')[:100] if payload.get('prompt') else 'N/A'}...")
            logger.info(f"Scene ID: {payload.get('scene_id')}")
            
            previous_contexts = payload.get('previous_contexts', [])
            if previous_contexts:
                logger.info(f"Previous contexts: {len(previous_contexts)} scenes")
            
            session = get_db_session()
            inbox_repo = InboxRepository(session)
            
            story_uuid = payload.get('story_uuid')
            scene_number = payload.get('scene_number')
            scene_id = payload.get('scene_id')
            
            idempotency_key = None
            if story_uuid and scene_number:
                idempotency_key = f"prompt.extracted:{story_uuid}:{scene_number}"
            elif scene_id:
                idempotency_key = f"prompt.extracted:scene_id:{scene_id}"
            
            inbox_event = inbox_repo.save_event(
                event_type=event_type,
                payload=payload,
                idempotency_key=idempotency_key
            )
            
            if inbox_event:
                logger.info(f"Saved to inbox (ID: {inbox_event.id})")
            else:
                logger.info(f"Event already processed (duplicate, idempotency_key: {idempotency_key})")
            
            message.ack()
            logger.info("Message acknowledged successfully")
            
        except Exception as e:
            logger.error(f"Error saving message to inbox: {e}")
            import traceback
            logger.error(traceback.format_exc())
            message.reject(requeue=True)
        finally:
            if session:
                session.close()
    
    def start(self):
        """Запускает консьюмер"""
        logger.info("Starting PromptExtractedConsumer...")
        logger.info(f"Connecting to broker: {self.broker_url}")
        logger.info(f"Exchange: {self.exchange.name}")
        logger.info(f"Queue: {self.queue.name}")
        logger.info(f"Routing key: {self.queue.routing_key}")
        
        with Connection(self.broker_url) as conn:
            with conn.Consumer(
                queues=[self.queue],
                callbacks=[self.handle_message],
                accept=['json']
            ) as consumer:
                logger.info("Consumer started. Waiting for messages...")
                try:
                    while True:
                        try:
                            conn.drain_events(timeout=1)
                        except TimeoutError:
                            pass
                except KeyboardInterrupt:
                    logger.info("Consumer stopped by user")


def main():
    consumer = PromptExtractedConsumer(get_broker_url())
    consumer.start()


if __name__ == '__main__':
    main()
