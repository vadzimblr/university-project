from datetime import datetime
from typing import Any, Dict, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from domain.entities.outbox_event import OutboxEvent
from domain.events.base import BaseEvent


def serialize_for_json(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_for_json(v) for v in value]
    if isinstance(value, dict):
        return {k: serialize_for_json(v) for k, v in value.items()}
    return value


class OutboxRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_event(
            self,
            event: Union[BaseEvent, str],
            payload: Optional[Dict[str, Any]] = None,
            commit: bool = True
    ) -> OutboxEvent:
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

        self.db_session.add(outbox_event)

        if commit:
            self.db_session.commit()
            self.db_session.refresh(outbox_event)
        else:
            self.db_session.flush()

        return outbox_event

    def get_unpublished_events(self, limit: int = 100) -> list[OutboxEvent]:
        return (
            self.db_session.query(OutboxEvent)
            .filter(OutboxEvent.published == False)
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .all()
        )

    def mark_as_published(self, event_id: UUID) -> bool:
        event = self.db_session.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            return False

        event.published = True
        event.published_at = datetime.utcnow()
        self.db_session.commit()
        return True

    def increment_retry_count(self, event_id: UUID, error_message: str) -> bool:
        event = self.db_session.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            return False

        event.retry_count += 1
        event.last_error = error_message
        self.db_session.commit()
        return True

    def get_failed_events(self, max_retries: int = 3) -> list[OutboxEvent]:
        return (
            self.db_session.query(OutboxEvent)
            .filter(
                OutboxEvent.published == False,
                OutboxEvent.retry_count >= max_retries
            )
            .all()
        )

    def delete_published_events(self, older_than_days: int = 7) -> int:
        from datetime import timedelta

        query = self.db_session.query(OutboxEvent).filter(OutboxEvent.published == True)

        if older_than_days > 0:
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            query = query.filter(OutboxEvent.published_at < cutoff_date)

        deleted = query.delete()
        self.db_session.commit()
        return deleted
