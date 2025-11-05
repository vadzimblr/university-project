from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.models.entities.OutboxEvent import OutboxEvent
from app.events.base import BaseEvent


def serialize_for_json(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, list):
        return [serialize_for_json(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_for_json(v) for k, v in value.items()}
    return value


class OutboxRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(
        self, 
        event: Union[BaseEvent, str],
        payload: Optional[Dict[str, Any]] = None,
        session: Optional[Session] = None
    ) -> OutboxEvent:
        db = session or self.db
        
        if isinstance(event, BaseEvent):
            event_type = event.event_type
            event_payload = event.to_payload()
        else:
            event_type = event
            event_payload = payload or {}
        
        serialized_payload = serialize_for_json(event_payload)
        
        outbox_event = OutboxEvent(
            event_type=event_type,
            payload=serialized_payload,
            published=False,
            retry_count=0
        )
        db.add(outbox_event)
        
        if session is None:
            db.commit()
            db.refresh(outbox_event)
        
        return outbox_event
    
    def get_unpublished_events(self, limit: int = 100) -> List[OutboxEvent]:
        return (
            self.db.query(OutboxEvent)
            .filter(OutboxEvent.published == False)
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .all()
        )
    
    def mark_as_published(self, event_id: UUID, commit: bool = True) -> bool:
        event = self.db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.published = True
        event.published_at = datetime.utcnow()
        
        if commit:
            self.db.commit()
        
        return True
    
    def mark_multiple_as_published(self, event_ids: List[UUID]) -> int:
        if not event_ids:
            return 0
        
        now = datetime.utcnow()
        updated = (
            self.db.query(OutboxEvent)
            .filter(OutboxEvent.id.in_(event_ids))
            .update(
                {
                    'published': True,
                    'published_at': now
                },
                synchronize_session=False
            )
        )
        self.db.commit()
        return updated
    
    def increment_retry_count(self, event_id: UUID, error_message: str) -> bool:
        event = self.db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.retry_count += 1
        event.last_error = error_message
        self.db.commit()
        return True
    
    def get_failed_events(self, max_retries: int = 3) -> List[OutboxEvent]:
        return (
            self.db.query(OutboxEvent)
            .filter(
                OutboxEvent.published == False,
                OutboxEvent.retry_count >= max_retries
            )
            .all()
        )

    def delete_published_events(self, older_than_days: int = 7) -> int:
        from datetime import timedelta, datetime
        query = self.db.query(OutboxEvent).filter(OutboxEvent.published == True)

        if older_than_days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            query = query.filter(OutboxEvent.published_at < cutoff_date)

        deleted = query.delete()
        self.db.commit()
        return deleted
