from typing import Protocol, Dict, Any

from aiohttp import ClientResponse


class LLMInterface(Protocol):

    async def ask(
            self,
            system: str,
            question: str,
            temperature: float = 0.1,
            max_tokens: int = 500
    ) -> str:
        raise NotImplementedError()

    @staticmethod
    async def _analyze_errors(response: ClientResponse) -> None:
        raise NotImplementedError()

    @staticmethod
    def _validate_response(data: Dict[str, Any]) -> str:
        raise NotImplementedError()

    @staticmethod
    def extract_json_from_text(text: str) -> Dict[str, Any]:
        raise NotImplementedError()
