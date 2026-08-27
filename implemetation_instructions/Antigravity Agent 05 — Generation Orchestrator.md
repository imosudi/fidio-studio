You are the generation-pipeline orchestration agent.

Read the domain model, API contracts, AI planner contract and infrastructure documentation.

Implement the asynchronous generation pipeline.

PIPELINE:

Generation Request
        |
        v
Validation
        |
        v
AI Planning
        |
        v
Structured Generation Plan
        |
        v
Scene/Asset Generation
        |
        v
Asset Validation
        |
        v
Audio/Narration Processing
        |
        v
Video Composition
        |
        v
Final Render
        |
        v
Persist Metadata
        |
        v
Completed

REQUIREMENTS:
- Generation must be asynchronous.
- API requests must not block while media is being generated.
- Each pipeline stage must have explicit state.
- Jobs must be retryable.
- Failed stages must expose meaningful error information.
- Pipeline execution must be resumable where practical.
- Implement idempotency.
- Avoid duplicate provider calls after worker retries.
- Persist intermediate state.
- Emit structured events/logs.
- Support cancellation where the architecture specifies it.

WORKER ARCHITECTURE:
Create:
- job dispatcher
- worker
- pipeline executor
- stage handlers
- retry policy
- dead-letter/failure handling where appropriate

MODEL:
Each stage should implement a consistent contract:

input
→ execute
→ validate output
→ persist result
→ update job state

Do not put provider-specific implementation inside orchestration logic.

Create mock generation adapters so the complete pipeline can be tested without spending money on external AI providers.

TEST:
- successful pipeline
- failed planning
- failed scene generation
- retry
- worker restart
- duplicate delivery
- cancellation
- partial pipeline recovery
- invalid generated media
- final render failure

The pipeline must remain modular enough that image, video, audio and future providers can be replaced independently.