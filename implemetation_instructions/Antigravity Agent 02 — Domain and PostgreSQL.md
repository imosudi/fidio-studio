You are the domain-model and persistence agent.

Read AGENTS.md and all architecture artifacts before making changes.

Implement the MVP domain model using PostgreSQL.

CORE ENTITIES SHOULD INCLUDE, AS APPROPRIATE TO THE ARCHITECTURE:
- User
- Project
- ProjectAsset
- Prompt/GenerationRequest
- GenerationPlan
- Scene
- GenerationJob
- JobStep
- MediaAsset
- Render
- ProviderInvocation
- API usage/cost metadata
- Audit/event records where justified

REQUIREMENTS:
- Use explicit primary keys.
- Use UTC timestamps.
- Add appropriate indexes.
- Model lifecycle/state transitions explicitly.
- Use database constraints where they protect invariants.
- Avoid storing media binaries in PostgreSQL.
- Store object-storage keys and metadata instead.
- Preserve provider request/response metadata necessary for debugging.
- Avoid storing secrets.
- Design the schema so generations are reproducible where possible.

IMPLEMENT:
1. ORM/domain models.
2. Migrations.
3. Repositories/data-access layer.
4. Transaction boundaries.
5. State-transition logic.
6. Database tests.
7. Seed/development data only where useful.

PAY PARTICULAR ATTENTION TO:
- idempotency
- job retries
- concurrent workers
- orphaned assets
- failed jobs
- partially completed generation pipelines
- optimistic/pessimistic locking where necessary

Do not implement HTTP controllers in this task.
Do not implement AI provider integrations.