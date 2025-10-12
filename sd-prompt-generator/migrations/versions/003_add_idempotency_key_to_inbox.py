from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'inbox_events',
        sa.Column('idempotency_key', sa.String(length=255), nullable=True)
    )
    
    op.create_index(
        'ix_inbox_events_idempotency_key',
        'inbox_events',
        ['idempotency_key'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_inbox_events_idempotency_key', table_name='inbox_events')
    op.drop_column('inbox_events', 'idempotency_key')

