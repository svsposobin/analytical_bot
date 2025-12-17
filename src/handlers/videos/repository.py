from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.videos.queries.select import (
    select_total_videos_count,
    select_videos_count_by_creator_and_date,
    select_videos_count_with_views_above,
    select_total_views_growth_by_date,
    select_unique_videos_with_new_views_by_date, select_videos_count_by_creator_above_views
)


class AnalyticRepository:

    @staticmethod
    async def get_total_videos_count(
            session: AsyncSession
    ) -> int:
        """Получить общее количество видео в системе"""
        stmt = select_total_videos_count()

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result or 0  # type: ignore

    @staticmethod
    async def get_videos_count_by_creator_and_date(
            session: AsyncSession,
            creator_id: str,
            date_from: date,
            date_to: date
    ) -> int:
        """Получить количество видео у конкретного креатора за период"""
        dt_from, dt_to = (
            datetime.combine(date_from, datetime.min.time()),
            datetime.combine(date_to, datetime.max.time())
        )
        stmt: Executable = select_videos_count_by_creator_and_date(
            creator_id=creator_id,
            date_from=dt_from,
            date_to=dt_to
        )

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result or 0  # type: ignore

    @staticmethod
    async def get_videos_count_with_views_above(
            views: int,
            session: AsyncSession
    ) -> int:
        """Получить количество видео с просмотрами выше заданного порога"""
        stmt: Executable = select_videos_count_with_views_above(views=views)

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result or 0  # type: ignore

    @staticmethod
    async def get_total_views_growth_by_date(
            target_date: date,
            session: AsyncSession
    ) -> int:
        """Получить суммарный прирост просмотров за конкретную дату"""
        dt_from = datetime.combine(target_date, datetime.min.time())
        dt_to = dt_from + timedelta(days=1)
        stmt: Executable = select_total_views_growth_by_date(date_from=dt_from, date_to=dt_to)

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result if result is not None else 0  # type: ignore

    @staticmethod
    async def get_unique_videos_with_new_views_by_date(
            target_date: date,
            session: AsyncSession
    ) -> int:
        """Получить количество уникальных видео, получивших новые просмотры в дату"""
        dt_from = datetime.combine(target_date, datetime.min.time())
        dt_to = dt_from + timedelta(days=1)
        stmt: Executable = select_unique_videos_with_new_views_by_date(date_from=dt_from, date_to=dt_to)

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result or 0  # type: ignore

    @staticmethod
    async def get_videos_count_by_creator_above_views(
            creator_id: str,
            views: int,
            session: AsyncSession
    ) -> int:
        """Получить количество видео у креатора с просмотрами выше порога"""
        stmt: Executable = select_videos_count_by_creator_above_views(
            creator_id=creator_id,
            views=views
        )

        result: Result[Any] = await AnalyticRepository.__execute_scalar(stmt=stmt, session=session)
        return result or 0  # type: ignore

    @staticmethod
    async def __execute_scalar(stmt: Executable, session: AsyncSession) -> Result[Any]:
        """Выполняет скалярный запрос"""
        result: Result[Any] = await session.execute(statement=stmt)
        return result.scalar_one()
