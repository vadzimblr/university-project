from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uq_scenes_story_uuid_scene_number',
        'scenes',
        ['story_uuid', 'scene_number']
    )


def downgrade() -> None:
    op.drop_constraint(
        'uq_scenes_story_uuid_scene_number',
        'scenes',
        type_='unique'
    )

