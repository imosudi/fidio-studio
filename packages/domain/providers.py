from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T", bound=BaseModel)


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    model_config = ConfigDict(from_attributes=True)


class LLMResponse(BaseModel):
    content: str
    structured_data: Optional[Any] = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    model_name: str
    execution_time_seconds: float = 0.0
    estimated_cost_usd: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class LLMProvider(ABC):
    """Abstract interface for LLM providers (OpenRouter, Mock, etc.)."""

    @abstractmethod
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
        """Generate LLM response with optional structured Pydantic schema validation."""
        pass
