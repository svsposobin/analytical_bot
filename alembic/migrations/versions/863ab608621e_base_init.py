from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '863ab608621e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('videos',
                    sa.Column('id', sa.String(length=36), nullable=False, comment='Video ID'),
                    sa.Column('creator_id', sa.String(length=32), nullable=False),
                    sa.Column('video_created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('views_count', sa.Integer(), nullable=False),
                    sa.Column('likes_count', sa.Integer(), nullable=False),
                    sa.Column('comments_count', sa.Integer(), nullable=False),
                    sa.Column('reports_count', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('videos_creation_id', 'videos', ['creator_id'], unique=False)
    op.create_table('video_snapshots',
                    sa.Column('id', sa.String(length=36), nullable=False, comment='Snapshot ID'),
                    sa.Column('video_id', sa.String(length=36), nullable=False),
                    sa.Column('views_count', sa.Integer(), nullable=False),
                    sa.Column('likes_count', sa.Integer(), nullable=False),
                    sa.Column('comments_count', sa.Integer(), nullable=False),
                    sa.Column('reports_count', sa.Integer(), nullable=False),
                    sa.Column('delta_views_count', sa.Integer(), nullable=False),
                    sa.Column('delta_likes_count', sa.Integer(), nullable=False),
                    sa.Column('delta_comments_count', sa.Integer(), nullable=False),
                    sa.Column('delta_reports_count', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
                    sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('snapshots_created_at', 'video_snapshots', ['created_at'], unique=False)
    op.create_index('snapshots_video_id', 'video_snapshots', ['video_id'], unique=False)


def downgrade() -> None:
    op.drop_index('snapshots_video_id', table_name='video_snapshots')
    op.drop_index('snapshots_created_at', table_name='video_snapshots')
    op.drop_table('video_snapshots')
    op.drop_index('videos_creation_id', table_name='videos')
    op.drop_table('videos')
