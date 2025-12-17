from typing import Dict, List
from json import dumps as json_dumps


class LLMPrompter:
    CONTEXT_DESCRIPTIONS: Dict[str, Dict] = {
        "TotalCountVideos": {
            "description": "Запрос общего количества видео в системе",
            "examples": [
                "Сколько всего видео?",
                "Какое общее количество видео в системе?",
                "Сколько видео всего загружено?"
            ],
            "response_format": {
                "key_context": "TotalCountVideos",
                "context": None
            }
        },

        "CountVideosPerCreatorByDate": {
            "description": "Запрос количества видео у конкретного креатора за период",
            "examples": [
                "Сколько видео у креатора с id 123 вышло с 2023-01-01 по 2023-12-31?",
                "Количество видео креатора 456 с 1 января 2023 до 31 декабря 2023",
                "Сколько видео выпустил креатор 789 в период с 01.01.2023 по 31.12.2023?"
            ],
            "response_format": {
                "key_context": "CountVideosPerCreatorByDate",
                "context": {
                    "creator_id": "строка с ID креатора",
                    "date_from": "дата в формате YYYY-MM-DD (например: 2023-05-15)",
                    "date_to": "дата в формате YYYY-MM-DD (например: 2023-05-15)"
                }
            }
        },

        "CountVideosPerMoreViews": {
            "description": "Запрос количества видео с просмотрами выше заданного порога",
            "examples": [
                "Сколько видео набрало больше 1000 просмотров?",
                "Количество видео с более чем 50000 просмотров",
                "Сколько видео имеет просмотров больше 1 млн?"
            ],
            "response_format": {
                "key_context": "CountVideosPerMoreViews",
                "context": {
                    "views": "Целое число (int)"
                }
            }
        },

        "CountViewsGrewUPPerDate": {
            "description": "Запрос суммарного прироста просмотров за конкретную дату",
            "examples": [
                "На сколько просмотров выросли все видео 2023-05-15?",
                "Суммарный прирост просмотров всех видео за 15 мая 2023",
                "На сколько выросли просмотры всех видео в дату 2023-05-15?"
            ],
            "response_format": {
                "key_context": "CountViewsGrewUPPerDate",
                "context": {
                    "date": "дата в формате YYYY-MM-DD (например: 2023-05-15)"
                }
            }
        },

        "CountDifferentVideosForNewViewsPerDate": {
            "description": "Запрос количества уникальных видео, получивших новые просмотры в дату",
            "examples": [
                "Сколько разных видео получали новые просмотры 2023-04-20?",
                "Количество видео, которые получили новые просмотры в дату 20 апреля 2023",
                "Сколько видео получили новые просмотры 2023-04-20?"
            ],
            "response_format": {
                "key_context": "CountDifferentVideosForNewViewsPerDate",
                "context": {
                    "date": "дата в формате YYYY-MM-DD (например: 2023-05-15)"
                }
            }
        }
    }

    @classmethod
    def create_system_prompt(cls) -> str:
        prompt_parts: List = []
        prompt_parts.append(
            """
            Ты - аналитический ассистент, который распознает тип запроса пользователя о статистике видео.
            Доступные типы запросов:
            """
        )
        for key, info in cls.CONTEXT_DESCRIPTIONS.items():
            prompt_parts.append(f"\n{key}:")
            prompt_parts.append(f"  Описание: {info['description']}")
            prompt_parts.append("  Примеры:")
            for example in info['examples']:
                prompt_parts.append(f"    - {example}")
            prompt_parts.append(f"  Формат ответа: {json_dumps(info['response_format'], ensure_ascii=False)}")

        prompt_parts.append(
            """
            Правила:
            1. Определи, к какому типу относится запрос пользователя
            2. Если запрос точно соответствует одному из типов - верни JSON с соответствующим key_context
            3. Если в запросе есть параметры (ID креатора, даты, число просмотров) - извлеки их и верни в context
            4. Даты всегда преобразуй в формат YYYY-MM-DD (например: 2023-05-15)
            5. Числовые параметры преобразуй в числа
            6. Если запрос не соответствует ни одному типу - верни {
                "key_context": null,
                "context": "Запрос не распознан"
            }
            7. Отвечай ТОЛЬКО JSON, без пояснений

            Примеры ответов:
            {"key_context": "TotalCountVideos", "context": null}
            {"key_context": "CountVideosPerCreatorByDate", "context": {
                "creator_id": "123",
                "date_from": "2023-01-01",
                "date_to": "2023-12-31"
                }
            }
            {"key_context": null, "context": "Запрос не распознан"}
            """
        )
        return "\n".join(prompt_parts)

    @classmethod
    def create_user_prompt(cls, user_query: str) -> str:
        """Создает промпт с запросом пользователя"""
        return f"Запрос пользователя: {user_query}"
