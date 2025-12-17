from sqlalchemy.ext.asyncio import AsyncSession

from src.core.llms.context_processor import ContextProcessor

from src.core.llms.schemas import BaseResponse
from src.core.llms.setups.yandexgpt import YandexGPT
from src.core.root.config import service_config
from src.handlers.videos.repository import AnalyticRepository
from src.handlers.videos.schemas import (
    TotalCountVideos,
    CountVideosPerCreatorByDate,
    CountVideosPerMoreViews,
    CountViewsGrewUPPerDate,
    CountDifferentVideosForNewViewsPerDate, QueryResponse
)


class TextQueryHandler:
    def __init__(self, context_processor: ContextProcessor) -> None:
        self.context_processor: ContextProcessor = context_processor

    async def process_text_query(self, user_query: str, session: AsyncSession) -> QueryResponse:
        """
        Упрощенный вариант получения данных в зависимости от контекста, в идеале для полной лаконичности исп-ть не
        match/case, а getattr и динамические вызовы
        """
        result: QueryResponse = QueryResponse()

        try:
            query_schema: BaseResponse = await self.context_processor.process_query(user_query=user_query)
            if query_schema.error:
                result.details = f"❌ {query_schema.error}"
                return result

            match query_schema:
                case TotalCountVideos():
                    count: int = await AnalyticRepository.get_total_videos_count(session=session)
                    result.result = count

                case CountVideosPerCreatorByDate() as schema:
                    count: int = await AnalyticRepository.get_videos_count_by_creator_and_date(  # type: ignore
                        creator_id=schema.creator_id,
                        date_from=schema.date_from,
                        date_to=schema.date_to,
                        session=session
                    )
                    result.result = count

                case CountVideosPerMoreViews() as schema:
                    count: int = await AnalyticRepository.get_videos_count_with_views_above(  # type: ignore
                        views=schema.views,
                        session=session
                    )
                    result.result = count

                case CountViewsGrewUPPerDate() as schema:
                    total_growth: int = await AnalyticRepository.get_total_views_growth_by_date(
                        target_date=schema.date,
                        session=session
                    )
                    result.result = total_growth

                case CountDifferentVideosForNewViewsPerDate() as schema:
                    unique_videos: int = await AnalyticRepository.get_unique_videos_with_new_views_by_date(
                        target_date=schema.date,
                        session=session
                    )
                    result.result = unique_videos

                case _:
                    raise Exception("Неизвестный тип запроса")  # Переброс

            result.status = True

        except Exception as error:
            result.details = str(error)

        return result


text_query_handler: TextQueryHandler = TextQueryHandler(
    context_processor=ContextProcessor(llm_client=YandexGPT(auth_config=service_config.yandex_gpt_auth))
)
