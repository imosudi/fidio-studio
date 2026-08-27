You are the AI orchestration and OpenRouter integration agent.

Read all existing architecture and domain contracts before implementation.

OBJECTIVE:
Implement the AI planning layer that converts a user generation request into a structured, machine-readable video generation plan.

ARCHITECTURE:
Create provider-independent interfaces such as:

LLMProvider
ModelRouter
PromptExecutor
GenerationPlanner

Then implement OpenRouter as an infrastructure adapter.

DO NOT allow application/domain code to depend directly on OpenRouter-specific classes.

THE PLANNER MUST PRODUCE STRUCTURED OUTPUT SUCH AS:
- project-level intent
- title
- style
- target duration
- aspect ratio
- scenes
- scene descriptions
- narration/dialogue where applicable
- visual-generation prompts
- audio requirements
- transition requirements
- ordering
- estimated generation workload

Use strict schema validation for model output.

IMPLEMENT:
1. Provider interfaces.
2. OpenRouter adapter.
3. Request construction.
4. Structured output validation.
5. Model configuration.
6. Timeout handling.
7. Retry handling.
8. Rate-limit handling.
9. Provider error normalization.
10. Token/usage metadata capture.
11. Estimated cost metadata where available.
12. Prompt-template management.
13. Planner service.
14. Unit/integration tests.
15. Mock provider for deterministic tests.

CONFIGURATION:
All provider/model configuration must come from environment/configuration.

Do not hard-code model names into domain logic.

SECURITY:
- Never log API keys.
- Never persist secrets.
- Redact sensitive request data from logs where appropriate.

TEST WITH:
- valid model output
- malformed JSON
- missing fields
- provider timeout
- rate limiting
- provider failure
- retryable failure
- non-retryable failure

The output of this module must be deterministic enough that the downstream generation pipeline can consume it without interpreting free-form LLM text.