from typing import Dict, Any, Optional
from pydantic import ValidationError

from src.core.llms.interface import LLMInterface

from src.core.llms.prompter import LLMPrompter
from src.core.llms.schemas import LLMResponse, BaseResponse
from src.handlers.videos.schemas import SCHEMA_MAP


class ContextProcessor:
    """Обрабатывает запросы пользователя через LLM и преобразует в схемы"""

    def __init__(self, llm_client: LLMInterface):
        self.llm_client = llm_client
        self.prompter: LLMPrompter = LLMPrompter()
        self.system_prompt: str = self.prompter.create_system_prompt()

    async def process_query(self, user_query: str) -> BaseResponse:
        """
        Обрабатывает запрос пользователя:
        1. Отправляет в LLM
        2. Парсит ответ
        3. Валидирует через Pydantic
        4. Возвращает соответствующую схему
        """
        try:
            user_prompt: str = self.prompter.create_user_prompt(user_query=user_query)
            llm_response_text: str = await self.llm_client.ask(
                system=self.system_prompt,
                question=user_prompt,
                temperature=0.1,
                max_tokens=500
            )

            validation_json_data: Dict[str, Any] = self.llm_client.extract_json_from_text(text=llm_response_text)
            llm_response: LLMResponse = LLMResponse(**validation_json_data)

            return ContextProcessor._create_request_schema(llm_response=llm_response)

        except ValidationError as e:
            return BaseResponse(error=f"Ошибка валидации данных: {e}")
        except Exception as e:
            return BaseResponse(error=f"Ошибка обработки запроса: {e}")

    @staticmethod
    def _create_request_schema(llm_response: LLMResponse) -> BaseResponse:
        """Создает схему запроса на основе ответа LLM"""

        if not llm_response.key_context:
            error_msg: str = "Запрос не распознан"

            if isinstance(llm_response.context, str):
                error_msg = llm_response.context

            return BaseResponse(error=error_msg)

        schema_class: Optional[Any] = SCHEMA_MAP.get(llm_response.key_context, None)
        if not schema_class:
            return BaseResponse(error=f"Неизвестный тип запроса: {llm_response.key_context}")

        try:
            if llm_response.context and isinstance(llm_response.context, dict):
                return schema_class(**llm_response.context)
            else:
                return schema_class()

        except ValidationError as e:
            error_details = []
            for error in e.errors():
                field = " -> ".join([str(loc) for loc in error['loc']])
                error_details.append(f"{field}: {error['msg']}")

            error_message = f"Ошибка в параметрах запроса: {', '.join(error_details)}"
            return BaseResponse(error=error_message)
