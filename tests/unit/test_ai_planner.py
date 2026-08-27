import uuid
import pytest
from packages.domain.entities import User, Project, GenerationRequest, GenerationPlan, Scene
from packages.domain.plan_schema import GenerationPlanData, ScenePlanData
from packages.providers import DevMockLLMProvider, OpenRouterLLMProvider
from packages.generation import GenerationPlanner
from packages.shared.exceptions import (
    ProviderTimeoutException, ProviderRateLimitException, ProviderValidationException
)


@pytest.mark.asyncio
async def test_dev_mock_provider_generation():
    """Verify DevMockLLMProvider returns valid structured GenerationPlanData."""
    provider = DevMockLLMProvider()
    response = await provider.generate(
        prompt="A futuristic neon city with flying cars",
        schema=GenerationPlanData
    )

    assert response.structured_data is not None
    plan_data: GenerationPlanData = response.structured_data
    assert plan_data.title == "Fídíò AI Generated Teaser"
    assert len(plan_data.scenes) == 3
    assert plan_data.scenes[0].scene_index == 1
    assert response.token_usage.total_tokens == 770


@pytest.mark.asyncio
async def test_dev_mock_forced_timeout():
    """Verify timeout exception handling."""
    provider = DevMockLLMProvider(force_timeout=True)
    with pytest.raises(ProviderTimeoutException) as exc_info:
        await provider.generate(prompt="Test timeout", schema=GenerationPlanData)
    assert exc_info.value.code == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_dev_mock_forced_rate_limit():
    """Verify rate limit exception handling."""
    provider = DevMockLLMProvider(force_rate_limit=True)
    with pytest.raises(ProviderRateLimitException) as exc_info:
        await provider.generate(prompt="Test rate limit", schema=GenerationPlanData)
    assert exc_info.value.code == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_dev_mock_forced_malformed_json():
    """Verify JSON schema validation exception handling."""
    provider = DevMockLLMProvider(force_malformed_json=True)
    with pytest.raises(ProviderValidationException) as exc_info:
        await provider.generate(prompt="Test malformed JSON", schema=GenerationPlanData)
    assert exc_info.value.code == "PROVIDER_ERROR"


@pytest.mark.asyncio
async def test_generation_planner_service(monkeypatch):
    """Test GenerationPlanner generates and returns structured plan."""
    mock_provider = DevMockLLMProvider()
    planner = GenerationPlanner(provider=mock_provider)

    gen_request = GenerationRequest(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        prompt="A cinematic drone shot over snow-capped mountains",
        style="cinematic",
        target_duration_seconds=15,
        aspect_ratio="16:9"
    )

    # Mock AsyncSession for testing entity persistence
    added_entities = []

    class MockAsyncSession:
        def add(self, entity):
            added_entities.append(entity)

        async def flush(self):
            pass

    mock_session = MockAsyncSession()

    plan = await planner.generate_plan(gen_request, mock_session)

    assert plan is not None
    assert plan.generation_request_id == gen_request.id
    assert plan.title == "Fídíò AI Generated Teaser"
    assert "Creative video intent" in plan.summary

    # Check entities added to session (1 ProviderInvocation + 1 GenerationPlan + 3 Scenes)
    assert len(added_entities) == 5
