from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from ..models.entities.InboxEvent import InboxEvent


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
    
    def get_unprocessed_events(self, limit: int = 100, max_retries: int = 5, lock_timeout_minutes: int = 10) -> List[InboxEvent]:
        from datetime import timedelta
        now = datetime.utcnow()
        lock_until = now + timedelta(minutes=lock_timeout_minutes)
        
        events = (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == False,
                InboxEvent.retry_count < max_retries,
                (InboxEvent.locked_until == None) | (InboxEvent.locked_until < now)
            )
            .order_by(InboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
            .all()
        )
        
        for event in events:
            event.locked_until = lock_until
            event.updated_at = now
        
        self.db.commit()
        
        return events
    
    def mark_as_processed(self, event_id: UUID) -> bool:
        event = self.db.query(InboxEvent).filter(InboxEvent.id == event_id).first()
        if not event:
            return False
        
        event.processed = True
        event.processed_at = datetime.utcnow()
        event.locked_until = None
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
        event.locked_until = None
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
        max_retries: int = 5, 
        lock_timeout_minutes: int = 10
    ) -> List[InboxEvent]:
        import logging
        logger = logging.getLogger(__name__)
        
        from datetime import timedelta
        now = datetime.utcnow()
        lock_until = now + timedelta(minutes=lock_timeout_minutes)
        
        candidate_events = (
            self.db.query(InboxEvent)
            .filter(
                InboxEvent.processed == False,
                InboxEvent.retry_count < max_retries,
                (InboxEvent.locked_until == None) | (InboxEvent.locked_until < now)
            )
            .order_by(InboxEvent.story_uuid, InboxEvent.scene_number, InboxEvent.created_at)
            .with_for_update(skip_locked=True)
            .all()
        )
        
        logger.info(f"[Sequential] Found {len(candidate_events)} candidate events in inbox")
        
        processable_events = []
        
        for event in candidate_events:
            if len(processable_events) >= limit:
                break
            
            if not event.story_uuid or event.scene_number is None:
                logger.info(f"[Sequential] Event {event.id} - no story/scene, processable")
                processable_events.append(event)
                continue
            
            if event.scene_number == 1:
                logger.info(f"[Sequential] Event {event.id} - scene 1 for story {event.story_uuid}, processable")
                processable_events.append(event)
                continue
            
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
                logger.info(f"[Sequential] Event {event.id} - scene {event.scene_number} for story {event.story_uuid}, previous scene processed, processable")
                processable_events.append(event)
            else:
                logger.info(f"[Sequential] Event {event.id} - scene {event.scene_number} for story {event.story_uuid}, waiting for scene {event.scene_number - 1}")
        
        for event in processable_events:
            event.locked_until = lock_until
            event.updated_at = now
        
        self.db.commit()
        
        logger.info(f"[Sequential] Returning {len(processable_events)} processable events")
        
        return processable_events

