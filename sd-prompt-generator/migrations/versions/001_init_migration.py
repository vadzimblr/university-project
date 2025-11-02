from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('stories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stories_id'), 'stories', ['id'], unique=False)
    op.create_index(op.f('ix_stories_uuid'), 'stories', ['uuid'], unique=True)
    op.create_table('story_characters',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('story_uuid', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('first_appeared_scene', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['story_uuid'], ['stories.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_story_characters_id'), 'story_characters', ['id'], unique=False)
    op.create_table('story_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('story_uuid', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['story_uuid'], ['stories.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_story_locations_id'), 'story_locations', ['id'], unique=False)
    op.create_table('scenes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('story_uuid', sa.String(length=100), nullable=False),
    sa.Column('scene_number', sa.Integer(), nullable=False),
    sa.Column('scene_text', sa.Text(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.Column('processing_time', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['story_locations.id'], ),
    sa.ForeignKeyConstraint(['story_uuid'], ['stories.uuid'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scenes_id'), 'scenes', ['id'], unique=False)
    op.create_table('scene_characters',
    sa.Column('scene_id', sa.Integer(), nullable=False),
    sa.Column('character_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['character_id'], ['story_characters.id'], ),
    sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ),
    sa.PrimaryKeyConstraint('scene_id', 'character_id')
    )
    op.create_table('scene_results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('scene_id', sa.Integer(), nullable=False),
    sa.Column('characters_data', sa.JSON(), nullable=True),
    sa.Column('location_data', sa.JSON(), nullable=True),
    sa.Column('actions', sa.Text(), nullable=True),
    sa.Column('sd_prompt', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['scene_id'], ['scenes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scene_results_id'), 'scene_results', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scene_results_id'), table_name='scene_results')
    op.drop_table('scene_results')
    op.drop_table('scene_characters')
    op.drop_index(op.f('ix_scenes_id'), table_name='scenes')
    op.drop_table('scenes')
    op.drop_index(op.f('ix_story_locations_id'), table_name='story_locations')
    op.drop_table('story_locations')
    op.drop_index(op.f('ix_story_characters_id'), table_name='story_characters')
    op.drop_table('story_characters')
    op.drop_index(op.f('ix_stories_uuid'), table_name='stories')
    op.drop_index(op.f('ix_stories_id'), table_name='stories')
    op.drop_table('stories')
