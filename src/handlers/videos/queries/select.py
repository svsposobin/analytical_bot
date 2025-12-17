from datetime import datetime
from sqlalchemy import select, func, and_, Executable

from src.handlers.videos.models import Videos, VideoSnapshots


def select_total_videos_count() -> Executable:
    """Запрос общего количества видео"""
    return select(func.count(Videos.id))


def select_videos_count_by_creator_and_date(
        creator_id: str,
        date_from: datetime,
        date_to: datetime
) -> Executable:
    """Запрос количества видео у креатора за период"""
    return select(func.count(Videos.id)).where(
        and_(
            Videos.creator_id == creator_id,
            Videos.video_created_at >= date_from,
            Videos.video_created_at <= date_to
        )
    )


def select_videos_count_with_views_above(views: int) -> Executable:
    """Запрос количества видео с просмотрами выше порога"""
    return select(func.count(Videos.id)).where(
        Videos.views_count > views
    )


def select_total_views_growth_by_date(date_from: datetime, date_to: datetime) -> Executable:
    """Запрос суммарного прироста просмотров за дату"""
    return select(func.sum(VideoSnapshots.delta_views_count)).where(
        and_(
            VideoSnapshots.created_at >= date_from,
            VideoSnapshots.created_at < date_to
        )
    )


def select_unique_videos_with_new_views_by_date(
        date_from: datetime,
        date_to: datetime
) -> Executable:
    """Запрос уникальных видео с новыми просмотрами за дату"""
    subquery = select(VideoSnapshots.video_id).where(
        and_(
            VideoSnapshots.created_at >= date_from,
            VideoSnapshots.created_at < date_to,
            VideoSnapshots.delta_views_count > 0
        )
    ).distinct()

    return select(func.count()).select_from(subquery.subquery())
