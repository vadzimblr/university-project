from datetime import datetime
from typing import Optional, Dict
from kombu import Connection, Exchange, Producer
from uuid import UUID

from app.repositories.outbox_repository import OutboxRepository
from app.utils.database import get_db_session
from app.utils.celery import get_broker_url
from app.events.base import EventRegistry


class EventPublisher:
    def __init__(self):
        self.broker_url = self._get_broker_url()
        self._exchanges_cache: Dict[str, Exchange] = {}
    
    def _get_broker_url(self) -> str:
        return get_broker_url()
    
    def _get_or_create_exchange(self, exchange_name: str) -> Exchange:
        if exchange_name not in self._exchanges_cache:
            self._exchanges_cache[exchange_name] = Exchange(
                exchange_name,
                type='topic',
                durable=True
            )
        return self._exchanges_cache[exchange_name]
    
    def _serialize_value(self, value):
        if isinstance(value, UUID):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        return value
    
    def _prepare_payload(self, payload: dict) -> dict:
        return {
            key: self._serialize_value(value)
            for key, value in payload.items()
        }

    def publish_event(
            self,
            event_type: str,
            payload: dict,
            exchange_name: str,
            routing_key: str
    ):
        exchange_name = str(exchange_name)
        routing_key = str(routing_key)
        event_type = str(event_type)

        exchange = self._get_or_create_exchange(exchange_name)

        message = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'payload': self._prepare_payload(payload)
        }

        with Connection(self.broker_url) as conn:
            with conn.channel() as channel:
                producer = Producer(channel)

                producer.publish(
                    message,
                    exchange=exchange,
                    routing_key=routing_key,
                    declare=[exchange],
                    serializer='json',
                    delivery_mode=2,
                    retry=True,
                    retry_policy={
                        'max_retries': 3,
                        'interval_start': 0,
                        'interval_step': 2,
                        'interval_max': 30,
                    }
                )

    def process_outbox_events(self, batch_size: int = 100) -> dict:
        session = get_db_session()
        outbox_repo = OutboxRepository(session)
        
        stats = {
            'processed': 0,
            'published': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            events = outbox_repo.get_unpublished_events(limit=batch_size)
            stats['processed'] = len(events)
            
            if not events:
                return stats
            
            published_event_ids = []
            
            for event in events:
                try:
                    event_class = EventRegistry.get_event_class(event.event_type)
                    if not event_class:
                        raise ValueError(f"Unknown event type: {event.event_type}")

                    exchange_name = str(event_class.get_exchange_name())
                    routing_key = str(event_class.get_routing_key())

                    self.publish_event(
                        event_type=str(event.event_type),
                        payload=event.payload,
                        exchange_name=exchange_name,
                        routing_key=routing_key
                    )

                    published_event_ids.append(event.id)
                    stats['published'] += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    stats['failed'] += 1
                    stats['errors'].append({
                        'event_id': str(event.id),
                        'error': error_msg
                    })

                    import traceback
                    print(f"Error publishing event {event.id}: {error_msg}")
                    print(traceback.format_exc())

                    outbox_repo.increment_retry_count(event.id, error_msg)
            
            if published_event_ids:
                outbox_repo.mark_multiple_as_published(published_event_ids)
                print(f"Batch committed {len(published_event_ids)} events")
            
            return stats
            
        finally:
            session.close()
    
    def cleanup_old_events(self, older_than_days: int = 7) -> int:
        session = get_db_session()
        outbox_repo = OutboxRepository(session)
        
        try:
            deleted = outbox_repo.delete_published_events(older_than_days)
            print(f"Cleaned up {deleted} old outbox events")
            return deleted
        finally:
            session.close()


_publisher = None


def get_event_publisher() -> EventPublisher:
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()

    return _publisher


