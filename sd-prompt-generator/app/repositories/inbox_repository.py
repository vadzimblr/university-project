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
        idempotency_key: Optional[str] = None,
        story_uuid: Optional[str] = None,
        scene_number: Optional[int] = None
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
            idempotency_key=idempotency_key,
            story_uuid=story_uuid,
            scene_number=scene_number
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
    
    def get_unprocessed_events_sequential(
        self, 
        limit: int = 100, 
        max_retries: int = 5
    ) -> List[InboxEvent]:
        """
        Gets unprocessed events that can be processed in sequential order.
        For events with story_uuid and scene_number:
        - Scene 1 is always processable
        - Scene N is processable only if scene N-1 is already processed
        
        Events without story_uuid/scene_number are processed normally.
        """
        # Get candidate events
        candidate_events = (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == False,
                InboxEvent.retry_count < max_retries
            )
            .order_by(InboxEvent.story_uuid, InboxEvent.scene_number, InboxEvent.created_at)
            .with_for_update(skip_locked=True)
            .all()
        )
        
        processable_events = []
        
        for event in candidate_events:
            if len(processable_events) >= limit:
                break
            
            # Events without story_uuid/scene_number are always processable
            if not event.story_uuid or event.scene_number is None:
                processable_events.append(event)
                continue
            
            # Scene 1 is always processable
            if event.scene_number == 1:
                processable_events.append(event)
                continue
            
            # Check if previous scene is processed
            previous_scene_processed = (
                self.db.query(InboxEvent)
                .filter(
                    InboxEvent.story_uuid == event.story_uuid,
                    InboxEvent.scene_number == event.scene_number - 1,
                    InboxEvent.processed == True
                )
                .first()
            ) is not None
            
            if previous_scene_processed:
                processable_events.append(event)
        
        return processable_events
