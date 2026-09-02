import time
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from packages.domain.entities import (
    GenerationRequest, GenerationPlan, Scene, ProviderInvocation, JobStatus
)
from packages.domain.plan_schema import GenerationPlanData
from packages.domain.providers import LLMProvider
from packages.providers import OpenRouterLLMProvider, DevMockLLMProvider
from packages.shared.config import settings
from packages.shared.exceptions import ValidationException
from packages.shared.logging import logger

SYSTEM_PLANNING_PROMPT = """You are Fídíò Engine, an expert AI creative producer and video director.
Your objective is to convert user video prompts into structured, production-ready video generation plans.
Analyze the user's intent, visual style, target duration, and aspect ratio.
Break down the video into ordered, cinematic scenes.
For each scene, craft detailed image/video visual prompts, negative prompts, narration dialogue, background audio prompts, and transition types.
Return ONLY structured JSON matching the provided schema."""


class GenerationPlanner:
    """Orchestrates AI structured planning converting creative requests into GenerationPlans."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        if provider:
            self.provider = provider
        elif settings.USE_MOCK_PROVIDERS:
            logger.info("USE_MOCK_PROVIDERS=true. Initializing GenerationPlanner with DevMockLLMProvider.")
            self.provider = DevMockLLMProvider()
        elif settings.OPENROUTER_API_KEY:
            self.provider = OpenRouterLLMProvider()
        else:
            logger.info("OPENROUTER_API_KEY unavailable. Initializing GenerationPlanner with DevMockLLMProvider.")
            self.provider = DevMockLLMProvider()

    async def generate_plan(
        self,
        gen_request: GenerationRequest,
        db_session: AsyncSession,
        job_id: Optional[uuid.UUID] = None
    ) -> GenerationPlan:
        """Execute LLM planning call, parse structured plan, and persist entities."""
        logger.info(f"Generating creative plan for GenerationRequest ID={gen_request.id} prompt='{gen_request.prompt[:60]}...'")

        user_prompt = (
            f"Creative Request: {gen_request.prompt}\n"
            f"Visual Style: {gen_request.style}\n"
            f"Target Duration: {gen_request.target_duration_seconds} seconds\n"
            f"Aspect Ratio: {gen_request.aspect_ratio}"
        )

        start_time = time.time()

        # Execute LLM Provider Generation with Pydantic JSON Schema Validation
        llm_response = await self.provider.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PLANNING_PROMPT,
            schema=GenerationPlanData,
            model_name=settings.OPENROUTER_MODEL_PLANNING
        )

        plan_data: GenerationPlanData = llm_response.structured_data
        if not plan_data:
            raise ValidationException("LLM Provider failed to return structured GenerationPlanData")

        # 1. Persist ProviderInvocation Audit Log
        invocation = ProviderInvocation(
            job_id=job_id,
            provider_name="openrouter" if isinstance(self.provider, OpenRouterLLMProvider) else "dev_mock",
            model_name=llm_response.model_name,
            prompt_tokens=llm_response.token_usage.prompt_tokens,
            completion_tokens=llm_response.token_usage.completion_tokens,
            latency_ms=int(llm_response.execution_time_seconds * 1000),
            estimated_cost_usd=llm_response.estimated_cost_usd,
            response_status_code=200
        )
        db_session.add(invocation)

        # 2. Persist GenerationPlan entity
        plan = GenerationPlan(
            generation_request_id=gen_request.id,
            title=plan_data.title,
            summary=plan_data.intent,
            aspect_ratio=plan_data.aspect_ratio,
            total_estimated_duration_seconds=float(plan_data.target_duration_seconds),
            plan_metadata_json={
                "style": plan_data.style,
                "estimated_workload": plan_data.estimated_workload,
                "model": llm_response.model_name
            }
        )
        db_session.add(plan)
        await db_session.flush()

        # 3. Persist Scene entities
        for scene_data in plan_data.scenes:
            scene = Scene(
                generation_plan_id=plan.id,
                scene_number=scene_data.scene_index,
                title=f"Scene {scene_data.scene_index}",
                visual_prompt=scene_data.visual_prompt,
                narration_script=scene_data.narration_text,
                duration_seconds=float(scene_data.duration_seconds),
                transition_type=scene_data.transition,
                camera_movement="cinematic_pan"
            )
            db_session.add(scene)

        await db_session.flush()
        logger.info(f"Persisted GenerationPlan ID={plan.id} with {len(plan_data.scenes)} scenes.")
        return plan
