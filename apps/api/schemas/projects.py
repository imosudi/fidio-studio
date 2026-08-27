import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project title")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    aspect_ratio: str = Field("16:9", description="Video aspect ratio (e.g. 16:9, 9:16, 1:1)")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    aspect_ratio: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    aspect_ratio: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
