"""Add outbox_events table for reliable event publishing

Revision ID: 003
Revises: 16e198645b8e
Create Date: 2025-10-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '16e198645b8e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'outbox_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_outbox_events_event_type', 'outbox_events', ['event_type'], unique=False)
    op.create_index('ix_outbox_events_published', 'outbox_events', ['published'], unique=False)
    # Для быстрого поиска неопубликованных событий
    op.create_index('ix_outbox_events_published_created', 'outbox_events', ['published', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_outbox_events_published_created', table_name='outbox_events')
    op.drop_index('ix_outbox_events_published', table_name='outbox_events')
    op.drop_index('ix_outbox_events_event_type', table_name='outbox_events')
    op.drop_table('outbox_events')

