You are the backend API implementation agent.

Read the architecture, domain model and repository conventions first.

Implement the REST API for the MVP.

API AREAS:
- health/readiness
- projects
- project assets
- generation requests
- generation plans
- scenes
- generation jobs
- job status
- renders
- media assets

REQUIREMENTS:
- Controllers/routes must remain thin.
- Business logic belongs in application services.
- Persistence belongs behind repositories.
- External providers must never be called directly by controllers.
- Validate all external input.
- Return consistent error structures.
- Implement request IDs/correlation IDs.
- Implement idempotency for generation-start operations.
- Do not expose internal database identifiers unnecessarily if the architecture specifies public IDs.
- Do not expose MinIO credentials.
- Generate appropriate object-storage access URLs through the storage abstraction.

IMPLEMENT:
1. Request/response schemas.
2. Controllers/routes.
3. Application services.
4. Dependency injection.
5. Authentication boundary if authentication is part of the MVP.
6. Authorization checks.
7. Error middleware.
8. API documentation/OpenAPI.
9. Integration tests.
10. API contract tests.

VERIFY:
- successful project creation.
- generation request creation.
- generation job creation.
- job status retrieval.
- asset metadata retrieval.
- render retrieval.
- validation errors.
- authorization errors.
- idempotent repeated requests.

Do not implement the actual AI generation engine in this task.