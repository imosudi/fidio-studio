from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, ConfigDict


class GeneratedMediaResult(BaseModel):
    bucket_name: str
    object_key: str
    mime_type: str
    file_size_bytes: int
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class MediaProvider(ABC):
    """Abstract interface for multi-modal AI media generation providers."""

    @abstractmethod
    async def generate_visual(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> GeneratedMediaResult:
        pass

    @abstractmethod
    async def generate_audio(
        self,
        script: str,
        voice: Optional[str] = "natural"
    ) -> GeneratedMediaResult:
        pass
