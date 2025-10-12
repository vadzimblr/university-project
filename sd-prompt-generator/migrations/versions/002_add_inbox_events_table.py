from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = 'c87b1a533c8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'inbox_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_inbox_events_event_type', 'inbox_events', ['event_type'], unique=False)
    op.create_index('ix_inbox_events_processed', 'inbox_events', ['processed'], unique=False)
    op.create_index('ix_inbox_events_processed_created', 'inbox_events', ['processed', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_inbox_events_processed_created', table_name='inbox_events')
    op.drop_index('ix_inbox_events_processed', table_name='inbox_events')
    op.drop_index('ix_inbox_events_event_type', table_name='inbox_events')
    op.drop_table('inbox_events')

