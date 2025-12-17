from typing import Optional, Union, Dict, Any

from pydantic import BaseModel, ConfigDict


class LLMResponse(BaseModel):
    key_context: Optional[str] = None
    context: Optional[Union[Dict[str, Any], str]] = None

    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    error: Optional[str] = None


class YandexGPTAuth(BaseModel):
    api_key: str
    folder_id: str
