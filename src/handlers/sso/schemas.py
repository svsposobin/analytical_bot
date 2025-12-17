from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator


class VideoSnapshotSchema(BaseModel):
    id: str = Field(..., description="Snapshot ID")
    video_id: str = Field(..., description="Video ID")
    views_count: int = Field(..., ge=0)
    likes_count: int = Field(..., ge=0)
    comments_count: int = Field(..., ge=0)
    reports_count: int = Field(..., ge=0)
    delta_views_count: int = Field(..., description="Change in views")
    delta_likes_count: int = Field(..., description="Change in likes")
    delta_comments_count: int = Field(..., description="Change in comments")
    delta_reports_count: int = Field(..., description="Change in reports")
    created_at: datetime
    updated_at: datetime


class VideoSchema(BaseModel):
    id: str = Field(..., description="Video ID")
    creator_id: str = Field(..., description="Creator ID")
    video_created_at: datetime
    views_count: int = Field(..., ge=0)
    likes_count: int = Field(..., ge=0)
    comments_count: int = Field(..., ge=0)
    reports_count: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime
    snapshots: List[VideoSnapshotSchema] = Field(default_factory=list)

    @field_validator('creator_id', mode="before")  # noqa
    @classmethod
    def validate_creator_id(cls, v: str) -> str:
        if len(v) != 32:
            raise ValueError('creator_id must be exactly 32 characters')
        return v


class UploadJsonSchema(BaseModel):
    videos: List[VideoSchema] = Field(..., description="List of videos with snapshots")
