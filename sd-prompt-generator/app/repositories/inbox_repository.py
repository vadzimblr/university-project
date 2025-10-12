from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from app.models.entities.InboxEvent import InboxEvent


class InboxRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def save_event(
        self, 
        event_type: str, 
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None
    ) -> Optional[InboxEvent]:
        if idempotency_key:
            existing = (
                self.db.query(InboxEvent)
                .filter(InboxEvent.idempotency_key == idempotency_key)
                .first()
            )
            if existing:
                return None
        
        inbox_event = InboxEvent(
            event_type=event_type,
            payload=payload,
            processed=False,
            retry_count=0,
            idempotency_key=idempotency_key
        )
        self.db.add(inbox_event)
        self.db.commit()
        self.db.refresh(inbox_event)
        
        return inbox_event
    
    def get_unprocessed_events(self, limit: int = 100, max_retries: int = 5) -> List[InboxEvent]:
        return (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == False,
                InboxEvent.retry_count < max_retries
            )
            .order_by(InboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
            .all()
        )
    
    def mark_as_processed(self, event_id: UUID) -> bool:
        event = self.db.query(InboxEvent).filter(InboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.processed = True
        event.processed_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def increment_retry_count(self, event_id: UUID, error_message: str) -> bool:
        event = self.db.query(InboxEvent).filter(InboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.retry_count += 1
        event.last_error = error_message
        event.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def mark_as_failed(self, event_id: UUID, error_message: str) -> bool:
        event = self.db.query(InboxEvent).filter(InboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.processed = True
        event.processed_at = datetime.utcnow()
        event.last_error = f"FAILED after {event.retry_count} retries: {error_message}"
        self.db.commit()
        return True
    
    def get_failed_events(self, max_retries: int = 3) -> List[InboxEvent]:
        return (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == False,
                InboxEvent.retry_count >= max_retries
            )
            .all()
        )
    
    def delete_processed_events(self, older_than_days: int = 7) -> int:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        deleted = (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == True,
                InboxEvent.processed_at < cutoff_date
            )
            .delete()
        )
        self.db.commit()
        return deleted
