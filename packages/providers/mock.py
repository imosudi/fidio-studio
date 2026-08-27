import time
import json
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

from packages.domain.providers import LLMProvider, LLMResponse, TokenUsage
from packages.domain.plan_schema import GenerationPlanData, ScenePlanData
from packages.shared.exceptions import (
    ProviderTimeoutException, ProviderRateLimitException, ProviderValidationException
)
from packages.shared.logging import logger

T = TypeVar("T", bound=BaseModel)


class DevMockLLMProvider(LLMProvider):
    """Development and testing mock LLM provider for deterministic generation execution."""

    def __init__(
        self,
        force_timeout: bool = False,
        force_rate_limit: bool = False,
        force_malformed_json: bool = False
    ):
        self.force_timeout = force_timeout
        self.force_rate_limit = force_rate_limit
        self.force_malformed_json = force_malformed_json

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Type[T]] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        timeout_seconds: float = 30.0
    ) -> LLMResponse:
        start_time = time.time()
        logger.info(f"DevMockLLMProvider generating response for prompt: '{prompt[:50]}...'")

        if self.force_timeout:
            raise ProviderTimeoutException("DevMockLLMProvider", "Mock forced request timeout")

        if self.force_rate_limit:
            raise ProviderRateLimitException("DevMockLLMProvider", "Mock forced rate limit (HTTP 429)")

        if self.force_malformed_json:
            raw_text = "{"  # Invalid JSON syntax
            if schema:
                raise ProviderValidationException(
                    "DevMockLLMProvider",
                    "Failed to parse model output as JSON: Expecting value: line 1 column 2 (char 1)"
                )
            return LLMResponse(
                content=raw_text,
                model_name=model_name or "dev-mock-model",
                execution_time_seconds=round(time.time() - start_time, 3)
            )

        # Default Mock Plan Generation
        mock_plan = GenerationPlanData(
            intent=f"Creative video intent for prompt: '{prompt}'",
            title="Fídíò AI Generated Teaser",
            style="cinematic",
            target_duration_seconds=15,
            aspect_ratio="16:9",
            scenes=[
                ScenePlanData(
                    scene_index=1,
                    duration_seconds=5.0,
                    description="Opening shot introducing visual theme and dramatic atmosphere",
                    visual_prompt=f"Cinematic wide shot, {prompt}, dramatic lighting, 8k resolution",
                    negative_prompt="blurry, low quality, noise",
                    narration_text="Welcome to the realm of imagined creation.",
                    narration_voice="epic_narrator",
                    background_audio_prompt="Deep cinematic synth riser and ambient bass line",
                    transition="cut"
                ),
                ScenePlanData(
                    scene_index=2,
                    duration_seconds=5.0,
                    description="Medium close-up focusing on primary character or subject detail",
                    visual_prompt=f"Detailed close-up visual, {prompt}, hyperdetailed, photorealistic",
                    negative_prompt="distortion, artifacts",
                    narration_text="Where every detail takes form in real-time.",
                    narration_voice="epic_narrator",
                    background_audio_prompt="Pulsing techno rhythm with ambient sound effects",
                    transition="fade"
                ),
                ScenePlanData(
                    scene_index=3,
                    duration_seconds=5.0,
                    description="Climactic climax scene with energetic movement and title resolve",
                    visual_prompt=f"High dynamic visual reveal, {prompt}, vibrant glowing accents",
                    negative_prompt="dull colors, blur",
                    narration_text="Imagine. Create. Fídíò.",
                    narration_voice="epic_narrator",
                    background_audio_prompt="Resonant bass drop resolving into smooth fade-out",
                    transition="dissolve"
                )
            ],
            estimated_workload=3
        )

        content_json = mock_plan.model_dump_json(indent=2)
        structured_obj = mock_plan if schema == GenerationPlanData else None

        return LLMResponse(
            content=content_json,
            structured_data=structured_obj,
            token_usage=TokenUsage(
                prompt_tokens=350,
                completion_tokens=420,
                total_tokens=770
            ),
            model_name=model_name or "dev-mock-model",
            execution_time_seconds=round(time.time() - start_time, 3),
            estimated_cost_usd=0.0
        )
