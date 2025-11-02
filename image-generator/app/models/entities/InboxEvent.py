from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from ...utils.database import Base


class InboxEvent(Base):
    __tablename__ = "inbox_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)

    processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime)

    retry_count = Column(Integer, default=0, nullable=False)
    last_error = Column(Text)

    received_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<InboxEvent {self.event_type} processed={self.processed}>"
