import time
import json
import asyncio
from typing import Optional, Type, TypeVar, Dict, Any
import httpx
from pydantic import BaseModel, ValidationError

from packages.domain.providers import LLMProvider, LLMResponse, TokenUsage
from packages.shared.config import settings
from packages.shared.exceptions import (
    ProviderException, ProviderTimeoutException,
    ProviderRateLimitException, ProviderValidationException
)
from packages.shared.logging import logger

T = TypeVar("T", bound=BaseModel)


class OpenRouterLLMProvider(LLMProvider):
    """Infrastructure adapter for OpenRouter AI API integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_model: Optional[str] = None,
        max_retries: int = 3
    ):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = (base_url or settings.OPENROUTER_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.OPENROUTER_MODEL_PLANNING
        self.max_retries = max_retries

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
        target_model = model_name or self.default_model

        if not self.api_key:
            logger.warning("OpenRouter API key missing. Falling back to DevMockLLMProvider.")
            from packages.providers.mock import DevMockLLMProvider
            mock = DevMockLLMProvider()
            return await mock.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=schema,
                model_name=target_model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        user_prompt_content = prompt
        if schema:
            schema_json = json.dumps(schema.model_json_schema(), indent=2)
            user_prompt_content += f"\n\nIMPORTANT: Respond ONLY with a valid JSON object matching the following Pydantic JSON Schema:\n{schema_json}"
        
        messages.append({"role": "user", "content": user_prompt_content})

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if schema:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://fidio.site",
            "X-Title": "Fídíò Studio",
            "Content-Type": "application/json"
        }

        url = f"{self.base_url}/chat/completions"
        start_time = time.time()
        
        attempt = 0
        backoff = 1.0

        while attempt < self.max_retries:
            attempt += 1
            try:
                logger.info(f"OpenRouter API request attempt {attempt}/{self.max_retries} model='{target_model}'")
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 429:
                    logger.warning(f"OpenRouter rate limit 429 on attempt {attempt}. Retrying in {backoff}s...")
                    if attempt >= self.max_retries:
                        raise ProviderRateLimitException("OpenRouter", "Rate limit exceeded after retries")
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue

                if response.status_code >= 500:
                    logger.warning(f"OpenRouter server error {response.status_code} on attempt {attempt}.")
                    if attempt >= self.max_retries:
                        raise ProviderException("OpenRouter", f"Server error HTTP {response.status_code}")
                    await asyncio.sleep(backoff)
                    backoff *= 2.0
                    continue

                if response.status_code != 200:
                    raise ProviderException(
                        "OpenRouter",
                        f"API request failed with status code {response.status_code}: {response.text[:200]}"
                    )

                data = response.json()
                choice_content = data["choices"][0]["message"]["content"]

                # Extract Usage
                usage_raw = data.get("usage", {})
                token_usage = TokenUsage(
                    prompt_tokens=usage_raw.get("prompt_tokens", 0),
                    completion_tokens=usage_raw.get("completion_tokens", 0),
                    total_tokens=usage_raw.get("total_tokens", 0)
                )

                # Parse Structured Pydantic Output if Schema requested
                structured_data = None
                if schema:
                    try:
                        structured_data = schema.model_validate_json(choice_content)
                    except ValidationError as ve:
                        logger.error(f"Structured output JSON schema validation failed: {ve}")
                        raise ProviderValidationException(
                            "OpenRouter",
                            "Model output failed strict JSON schema validation",
                            details={"validation_error": str(ve), "raw_output": choice_content[:500]}
                        )

                execution_time = round(time.time() - start_time, 3)

                return LLMResponse(
                    content=choice_content,
                    structured_data=structured_data,
                    token_usage=token_usage,
                    model_name=target_model,
                    execution_time_seconds=execution_time,
                    estimated_cost_usd=0.0  # OpenRouter optional cost header mapping
                )

            except httpx.TimeoutException:
                logger.warning(f"OpenRouter request timeout on attempt {attempt}/{self.max_retries}")
                if attempt >= self.max_retries:
                    raise ProviderTimeoutException("OpenRouter", f"Request timed out after {timeout_seconds}s")
                await asyncio.sleep(backoff)
                backoff *= 2.0
            except (ProviderException, ProviderTimeoutException, ProviderRateLimitException, ProviderValidationException):
                raise
            except Exception as e:
                logger.error(f"Unexpected OpenRouter request error: {e}", exc_info=True)
                raise ProviderException("OpenRouter", str(e))

        raise ProviderException("OpenRouter", "Max execution retries exceeded")
