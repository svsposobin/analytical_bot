from datetime import date
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from src.core.llms.schemas import BaseResponse


class TotalCountVideos(BaseResponse):
    pass


class CountVideosPerCreatorByDate(BaseResponse):
    creator_id: str
    date_from: date
    date_to: date

    @field_validator('creator_id', mode="before")
    @classmethod
    def validate_creator_id(cls, v: Optional[str]) -> str:
        if v is None:
            raise ValueError("creator_id не может быть None")
        if not isinstance(v, str):
            raise ValueError(f"creator_id должен быть строкой, получен {type(v)}")

        creator_id = v.strip()
        if not creator_id:
            raise ValueError("creator_id не может быть пустым")

        return creator_id

    @field_validator('date_from', 'date_to', mode="before")
    @classmethod
    def validate_date_strings(cls, v: Any) -> str:
        """Преобразует входные значения в строку, если это необходимо"""
        if isinstance(v, date):
            return v.isoformat()
        elif isinstance(v, str):
            return v
        else:
            raise ValueError(f"Дата должна быть строкой или date, получен {type(v)}")

    @field_validator('date_to', mode="before")
    @classmethod
    def validate_dates(cls, v: date, info):
        values = info.data

        if not isinstance(v, date):
            raise ValueError(f"date_to должен быть date, получен {type(v)}")

        date_from = values.get('date_from')
        if date_from and isinstance(date_from, date):
            if v < date_from:
                raise ValueError("date_to должен быть после или равен date_from")
        return v


class CountVideosPerMoreViews(BaseResponse):
    views: int

    @field_validator('views', mode="before")
    @classmethod
    def validate_views(cls, v: int) -> int:
        if v < 0:
            raise ValueError("views не может быть отрицательным")
        return v


class CountViewsGrewUPPerDate(BaseResponse):
    date: date


class CountDifferentVideosForNewViewsPerDate(BaseResponse):
    date: date

class CountVideosPerCreatorAboveViews(BaseResponse):
    creator_id: str
    views: int

    @field_validator('creator_id', mode="before")
    @classmethod
    def validate_creator_id(cls, v: Optional[str]) -> str:
        if v is None:
            raise ValueError("creator_id не может быть None")
        if not isinstance(v, str):
            raise ValueError(f"creator_id должен быть строкой, получен {type(v)}")

        creator_id = v.strip()
        if not creator_id:
            raise ValueError("creator_id не может быть пустым")

        return creator_id

    @field_validator('views', mode="before")
    @classmethod
    def validate_views(cls, v: int) -> int:
        if v < 0:
            raise ValueError("views не может быть отрицательным")
        return v


class QueryResponse(BaseModel):
    status: bool = Field(default=False, description="Статус выполнения")
    result: Optional[Any] = Field(default=None, description="Результат запроса")
    details: Optional[str] = Field(default=None, description="Детали или ошибка")


SCHEMA_MAP: Dict[str, Any] = {
    "TotalCountVideos": TotalCountVideos,
    "CountVideosPerCreatorByDate": CountVideosPerCreatorByDate,
    "CountVideosPerMoreViews": CountVideosPerMoreViews,
    "CountViewsGrewUPPerDate": CountViewsGrewUPPerDate,
    "CountDifferentVideosForNewViewsPerDate": CountDifferentVideosForNewViewsPerDate,
    "CountVideosPerCreatorAboveViews": CountVideosPerCreatorAboveViews
}
