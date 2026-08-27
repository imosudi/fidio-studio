import uuid
import time
from typing import Optional
from packages.domain.media_providers import MediaProvider, GeneratedMediaResult
from packages.shared.config import settings
from packages.shared.exceptions import ProviderException
from packages.shared.logging import logger


class DevMockMediaProvider(MediaProvider):
    """Deterministic development mock media provider for visual, audio, and video generation."""

    def __init__(
        self,
        force_visual_failure: bool = False,
        force_audio_failure: bool = False,
        force_render_failure: bool = False
    ):
        self.force_visual_failure = force_visual_failure
        self.force_audio_failure = force_audio_failure
        self.force_render_failure = force_render_failure

    async def generate_visual(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> GeneratedMediaResult:
        logger.info(f"DevMockMediaProvider generating visual asset for prompt: '{prompt[:50]}...'")

        if self.force_visual_failure:
            raise ProviderException("DevMockMediaProvider", "Forced visual asset generation failure")

        asset_id = str(uuid.uuid4())
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_MEDIA,
            object_key=f"visuals/mock_{asset_id[:8]}.png",
            mime_type="image/png",
            file_size_bytes=1048576,  # 1 MB
            duration_seconds=5.0,
            width=1920 if aspect_ratio == "16:9" else 1080,
            height=1080 if aspect_ratio == "16:9" else 1920
        )

    async def generate_audio(
        self,
        script: str,
        voice: Optional[str] = "natural"
    ) -> GeneratedMediaResult:
        logger.info(f"DevMockMediaProvider generating narration audio script: '{script[:50]}...'")

        if self.force_audio_failure:
            raise ProviderException("DevMockMediaProvider", "Forced audio asset generation failure")

        asset_id = str(uuid.uuid4())
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_MEDIA,
            object_key=f"audio/mock_{asset_id[:8]}.mp3",
            mime_type="audio/mpeg",
            file_size_bytes=524288,  # 512 KB
            duration_seconds=5.0
        )

    async def render_video(
        self,
        plan_id: str,
        scenes_count: int,
        resolution: str = "1920x1080"
    ) -> GeneratedMediaResult:
        logger.info(f"DevMockMediaProvider composing final video render for plan_id={plan_id} ({scenes_count} scenes)")

        if self.force_render_failure:
            raise ProviderException("DevMockMediaProvider", "Forced video composition render failure")

        render_id = str(uuid.uuid4())
        return GeneratedMediaResult(
            bucket_name=settings.MINIO_BUCKET_RENDERS,
            object_key=f"renders/fidio_render_{render_id[:8]}.mp4",
            mime_type="video/mp4",
            file_size_bytes=15728640,  # 15 MB
            duration_seconds=scenes_count * 5.0,
            width=1920,
            height=1080
        )
