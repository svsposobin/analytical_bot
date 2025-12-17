from typing import List, Set, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.handlers.sso.schemas import UploadJsonSchema
from src.handlers.videos.models import Videos, VideoSnapshots


class UploadRepository:

    @staticmethod
    async def save_upload_data(session: AsyncSession, upload_data: UploadJsonSchema) -> Dict[str, Any]:
        """Сохраняет данные из JSON в базу и возвращает статистику"""
        stats: Dict[str, Any] = {
            'videos_processed': 0,
            'videos_created': 0,
            'snapshots_created': 0,
            'errors': []
        }

        video_ids: List[str] = [video.id for video in upload_data.videos]
        snapshot_ids: List[str] = []

        for video in upload_data.videos:
            snapshot_ids.extend([snapshot.id for snapshot in video.snapshots])  # noqa

        try:
            existing_videos: Set[str] = await UploadRepository.check_existing_videos(
                session=session,
                video_ids=video_ids
            )
            existing_snapshots: Set[str] = await UploadRepository.check_existing_snapshots(
                session=session,
                snapshot_ids=snapshot_ids
            )

            if existing_videos:
                raise ValueError(
                    f"Видео с ID {', '.join(list(existing_videos)[:5])} уже существуют в базе"
                )
            if existing_snapshots:
                raise ValueError(
                    f"Снапшоты с ID {', '.join(list(existing_snapshots)[:5])} уже существуют в базе"
                )

            videos_to_add = []
            for video_data in upload_data.videos:
                video: Videos = Videos(  # type: ignore
                    id=video_data.id,
                    creator_id=video_data.creator_id,
                    video_created_at=video_data.video_created_at,
                    views_count=video_data.views_count,
                    likes_count=video_data.likes_count,
                    comments_count=video_data.comments_count,
                    reports_count=video_data.reports_count,
                    created_at=video_data.created_at,
                    updated_at=video_data.updated_at
                )
                videos_to_add.append(video)
                stats['videos_created'] += 1

            session.add_all(videos_to_add)
            await session.flush()

            snapshots_to_add = []
            for video_data in upload_data.videos:
                for snapshot_data in video_data.snapshots:
                    snapshot: VideoSnapshots = VideoSnapshots(
                        id=snapshot_data.id,
                        video_id=snapshot_data.video_id,
                        views_count=snapshot_data.views_count,
                        likes_count=snapshot_data.likes_count,
                        comments_count=snapshot_data.comments_count,
                        reports_count=snapshot_data.reports_count,
                        delta_views_count=snapshot_data.delta_views_count,
                        delta_likes_count=snapshot_data.delta_likes_count,
                        delta_comments_count=snapshot_data.delta_comments_count,
                        delta_reports_count=snapshot_data.delta_reports_count,
                        created_at=snapshot_data.created_at,
                        updated_at=snapshot_data.updated_at
                    )
                    snapshots_to_add.append(snapshot)
                    stats['snapshots_created'] += 1

                stats['videos_processed'] += 1

            session.add_all(snapshots_to_add)

            await session.commit()
            return stats

        except IntegrityError as e:
            await session.rollback()
            raise ValueError(f"Ошибка целостности данных: {str(e)}")

    @staticmethod
    async def check_existing_videos(session: AsyncSession, video_ids: List[str]) -> Set[str]:
        """Проверяет, какие видео уже существуют в базе"""
        if not video_ids:
            return set()

        result = await session.execute(
            statement=select(Videos.id).where(Videos.id.in_(video_ids))
        )
        return {row[0] for row in result.fetchall()}

    @staticmethod
    async def check_existing_snapshots(session: AsyncSession, snapshot_ids: List[str]) -> Set[str]:
        """Проверяет, какие снапшоты уже существуют в базе"""
        if not snapshot_ids:
            return set()

        result = await session.execute(
            statement=select(VideoSnapshots.id).where(VideoSnapshots.id.in_(snapshot_ids))
        )
        return {row[0] for row in result.fetchall()}
