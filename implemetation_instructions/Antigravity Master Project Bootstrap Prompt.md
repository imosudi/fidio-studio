You are the principal software architect and technical lead for this project.

PROJECT:
Build the MVP of a modular AI video generation platform.
Brand:       Fídíò
Product:     Fídíò Studio
Repository:  fidio-studio (https://github.com/imosudi/fidio-studio)
Core engine: Fídíò Engine
API:         Fídíò API
Engine:      Fídíò Engine
Tagline:     Imagine. Create. Fídíò.
Brand promise: Imagine. Create. Fídíò.
Product descriptor: AI-powered creative production
Brand category: Intelligent creative technology
Python/package namespace:	fidio
Docker prefix:	fidio-*
Brand architecture:
FÍDÍÒ
│
├── Studio
│   └── Creator application
│
├── Engine
│   └── AI generation/orchestration
│
├── API
│   └── Developer integration
│
├── Cloud
│   └── Hosted platform
│
└── Enterprise
    └── Business/enterprise deployment
    
    
                 FÍDÍÒ STUDIO
                      │
                    Idea
                      ↓
               AI Understanding
                      ↓
                Creative Plan
                      ↓
              ┌───────┼───────┐
              ↓       ↓       ↓
            Visual   Audio   Voice
              │       │       │
              └───────┼───────┘
                      ↓
                 Composition
                      ↓
                 Final Video

OBJECTIVE:
Create a production-oriented MVP that allows a user to:
1. Create a video project.
2. Provide a text/video-generation request.
3. Transform the request into a structured generation plan.
4. Generate or request AI media through configurable model providers.
5. Store generated media and intermediate assets.
6. Track generation jobs and their states.
7. Assemble generated assets into a final video.
8. Preview and download the resulting video.
9. Inspect job status, errors, metadata, and generation history.

ARCHITECTURAL PRINCIPLES:
- Modular monolith for the MVP, with clear internal service boundaries.
- Design modules so selected components can later become independent microservices.
- PostgreSQL is external to the container stack.
- MinIO is the S3-compatible object-storage layer for the MVP.
- All other application infrastructure should be containerised.
- OpenRouter is the primary LLM/model-routing integration.
- Provider-specific AI integrations must be abstracted behind interfaces.
- Never hard-code a single AI provider into domain logic.
- Long-running generation must be asynchronous.
- API operations must be stateless.
- Persist job state in PostgreSQL.
- Persist generated/intermediate media in MinIO.
- Use signed/object-storage URLs rather than exposing internal storage paths.
- Configuration must be environment-driven.
- Secrets must never be committed to source control.
- Every external provider must have timeout, retry, failure and observability handling.
- The MVP must remain runnable on a single development machine using Docker Compose except for PostgreSQL.

EXPECTED HIGH-LEVEL MODULES:
- API
- Authentication/user/project management
- Project management
- Prompt/script planning
- Generation orchestration
- AI provider abstraction
- OpenRouter integration
- Media asset management
- Object storage abstraction
- Video composition/rendering
- Job queue/worker
- Notifications/status
- Observability
- Configuration
- Database persistence

TECHNICAL DIRECTION:
Use the repository's existing technology choices if already established.
Do not replace an existing technology merely because you prefer another one.

If the repository is empty, first propose a concrete stack suitable for:
- Python backend
- REST API
- asynchronous workers
- PostgreSQL
- MinIO
- Docker Compose
- FFmpeg-based media processing
- modern web frontend

BEFORE WRITING IMPLEMENTATION CODE:
1. Inspect the complete repository.
2. Identify existing files, conventions and technology choices.
3. Produce an architecture assessment.
4. Identify missing components.
5. Create/update:
   - AGENTS.md
   - architecture documentation
   - module boundaries
   - API conventions
   - database conventions
   - development commands
   - testing strategy
6. Produce an implementation plan broken into independently executable tasks.

DO NOT:
- Rewrite unrelated existing code.
- Introduce unnecessary microservices.
- Introduce Kubernetes for the MVP.
- Replace PostgreSQL.
- Replace MinIO with another storage provider.
- Couple business logic directly to OpenRouter.
- Put provider-specific code into API controllers.
- Store binary media inside PostgreSQL.
- Implement fake production integrations without clearly marking them as development adapters.

DEFINITION OF DONE:
The repository has a documented architecture, explicit module boundaries, development conventions, environment configuration strategy, test strategy, and a dependency graph that later agents can implement without making architectural decisions independently.

Do not implement the complete application during this task.
First establish the architecture and implementation contract.


