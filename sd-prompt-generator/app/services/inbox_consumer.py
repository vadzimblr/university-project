import os
import json
from kombu import Connection, Queue, Exchange, Consumer
from kombu.mixins import ConsumerMixin

from app.repositories.inbox_repository import InboxRepository
from app.database.connection import get_db_session
from ..utils.celery import get_broker_url

class SceneEventsInboxConsumer(ConsumerMixin):
    def __init__(self, connection):
        self.connection = connection
        
        self.scene_saved_exchange = Exchange(
            'scene_saved_events',
            type='topic',
            durable=True
        )
        
        self.scene_saved_queue = Queue(
            'sd_prompt_generator_scene_saved',
            exchange=self.scene_saved_exchange,
            routing_key='scene.saved',
            durable=True,
            auto_delete=False
        )
    
    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=[self.scene_saved_queue],
                callbacks=[self.on_message],
                accept=['json'],
                prefetch_count=1
            )
        ]
    
    def on_message(self, body, message):
        session = None
        try:
            session = get_db_session()
            inbox_repo = InboxRepository(session)
            
            event_type = body.get('event_type')
            payload = body.get('payload', {})
            timestamp = body.get('timestamp')
            
            idempotency_key = None
            story_uuid = None
            scene_number = None
            
            if event_type == 'scene.saved':
                doc_id = payload.get('document_id')
                scene_num = payload.get('scene_number')
                if doc_id and scene_num:
                    idempotency_key = f"scene.saved:{doc_id}:{scene_num}"
                    story_uuid = doc_id
                    scene_number = scene_num
            
            print(f"\nReceived event: {event_type} [{timestamp}]")
            print(f"  Scene #{payload.get('scene_number')}, Document: {payload.get('document_id')}")
            
            inbox_event = inbox_repo.save_event(
                event_type=event_type,
                payload=payload,
                idempotency_key=idempotency_key,
                story_uuid=story_uuid,
                scene_number=scene_number
            )
            
            if inbox_event:
                print(f"  Saved to inbox (ID: {inbox_event.id})")
            else:
                print(f"  Event already processed (duplicate)")
            
            message.ack()
            
        except Exception as e:
            print(f"  Error saving to inbox: {e}")
            message.reject(requeue=True)
        finally:
            if session:
                session.close()


def get_rabbitmq_connection():
    return Connection(get_broker_url())
