from datetime import datetime

from sqlalchemy import DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String

from src.core.databases.relational.basemeta import BaseMeta


class Videos(BaseMeta):
    __tablename__ = 'videos'
    __table_args__ = (
        Index("videos_creation_id", "creator_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, comment="Video ID")
    creator_id: Mapped[str] = mapped_column(String(32), nullable=False)
    video_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class VideoSnapshots(BaseMeta):
    __tablename__ = 'video_snapshots'
    __table_args__ = (
        Index("snapshots_video_id", "video_id"),
        Index("snapshots_created_at", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, comment="Snapshot ID")
    video_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False
    )
    views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reports_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_views_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_likes_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_comments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    delta_reports_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
