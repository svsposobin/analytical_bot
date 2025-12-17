from json import loads, JSONDecodeError
from re import DOTALL, search as re_search, Match
from typing import Dict, Any, Optional
from aiohttp import ClientSession, ClientError, ClientResponse

from src.core.llms.exceptions import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMContentError,
    LLMConnectionError,
    JSONParseError
)
from src.core.llms.schemas import YandexGPTAuth


class YandexGPT:
    def __init__(self, auth_config: YandexGPTAuth):
        self._auth_config = auth_config
        self.base_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    async def ask(
            self,
            system: str,
            question: str,
            temperature: float = 0.6,
            max_tokens: int = 1000
    ) -> str:
        headers: Dict[str, Any] = {
            "Authorization": f"Api-Key {self._auth_config.api_key}",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "modelUri": f"gpt://{self._auth_config.folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": max(0.0, min(1.0, temperature)),
                "maxTokens": max_tokens
            },
            "messages": [
                {
                    "role": "system",
                    "text": system
                },
                {
                    "role": "user",
                    "text": question
                }
            ]
        }

        try:
            async with ClientSession() as session:
                async with session.post(
                        self.base_url,
                        headers=headers,
                        json=payload,
                        timeout=30  # type: ignore
                ) as response:
                    if response.status >= 400:
                        await self._analyze_errors(response=response)

                    data: Dict[str, Any] = await response.json()
                    return self._validate_response(data=data)

        except ClientError as e:
            raise LLMConnectionError(f"Сетевая ошибка: {e}")
        except TimeoutError:
            raise LLMConnectionError("Таймаут запроса (30 секунд)")
        except JSONDecodeError as e:
            raise LLMContentError(f"Некорректный JSON в ответе: {e}")

    @staticmethod
    async def _analyze_errors(response: ClientResponse) -> None:
        status_code = response.status

        try:
            error_data: Dict[str, Any] = await response.json()
            error_msg: Optional[str] = error_data.get("message", str(error_data))
        except (JSONDecodeError, ClientError):
            error_msg = await response.text()

        if not isinstance(error_msg, str):
            error_msg = str(error_msg)
        if len(error_msg) > 200:
            error_msg = error_msg[:197] + "..."

        if status_code == 401:
            raise LLMAuthenticationError(f"Неверный API ключ: {error_msg}")
        elif status_code == 429:
            raise LLMRateLimitError(f"Превышен лимит запросов: {error_msg}")
        elif 400 <= status_code < 500:
            raise LLMContentError(f"Ошибка клиента ({status_code}): {error_msg}")
        elif status_code >= 500:
            raise LLMConnectionError(f"Ошибка сервера ({status_code}): {error_msg}")

    @staticmethod
    def _validate_response(data: Dict[str, Any]) -> str:
        if "result" not in data:
            raise LLMContentError("Ответ API не содержит 'result'")

        result = data["result"]
        if "alternatives" not in result:
            raise LLMContentError("Ответ API не содержит 'alternatives'")

        alternatives = result["alternatives"]
        if not alternatives or not isinstance(alternatives, list):
            raise LLMContentError("'alternatives' пуст или не является списком")

        first_alternative = alternatives[0]
        if "message" not in first_alternative:
            raise LLMContentError("Alternative не содержит 'message'")

        message = first_alternative["message"]
        if "text" not in message:
            raise LLMContentError("Message не содержит 'text'")

        text = message["text"]
        if not isinstance(text, str):
            raise LLMContentError("Text должен быть строкой")

        if not text.strip():
            raise LLMContentError("Получен пустой ответ от модели")

        return text

    @staticmethod
    def extract_json_from_text(text: str) -> Dict[str, Any]:
        text = text.strip()

        if text.startswith("```json"):
            text = text[7:].strip()
        elif text.startswith("```"):
            text = text[3:].strip()

        if text.endswith("```"):
            text = text[:-3].strip()

        match: Match = re_search(pattern=r'\{.*\}', string=text, flags=DOTALL)  # type: ignore
        if not match:
            raise JSONParseError(f"JSON не найден в тексте. Начало текста: {text[:100]}...")

        try:
            return loads(match.group(0))
        except JSONDecodeError as e:
            raise JSONParseError(f"Ошибка парсинга JSON: {e}")
