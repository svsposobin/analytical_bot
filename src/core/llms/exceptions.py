class LLMError(Exception):
    """Базовое исключение для ошибок LLM"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LLMAuthenticationError(LLMError):
    """Ошибка аутентификации"""
    pass


class LLMRateLimitError(LLMError):
    """Превышен лимит запросов"""
    pass


class LLMContentError(LLMError):
    """Ошибка в содержимом"""
    pass


class LLMConnectionError(LLMError):
    """Ошибка подключения"""
    pass


class JSONParseError(LLMError):
    """Ошибка парсинга JSON"""
    pass
