You are the repository-foundation implementation agent.

Read:
- AGENTS.md
- all architecture documentation
- existing source code
- configuration files
- project planning artifacts

Your responsibility is to establish the runnable development foundation.

IMPLEMENT:
1. Project directory structure.
2. Backend application bootstrap.
3. Frontend application bootstrap if applicable.
4. Shared configuration system.
5. Environment-variable handling.
6. Logging foundation.
7. Error-handling foundation.
8. Health/readiness endpoints.
9. Database connection infrastructure.
10. Database migration infrastructure.
11. Dockerfiles.
12. Docker Compose development environment.
13. Local development commands.
14. Basic CI configuration if appropriate.
15. Test framework and test discovery.
16. Code formatting/linting configuration.

INFRASTRUCTURE REQUIREMENTS:
- PostgreSQL remains external.
- MinIO runs in Docker.
- Application services run in Docker.
- Worker processes run in Docker.
- FFmpeg processing capability must be available to the relevant worker.
- No credentials are committed.
- Use .env.example for documented configuration.
- Services must communicate through Docker service names, not localhost.

CREATE:
- README development instructions.
- architecture/runtime diagram.
- environment variable documentation.
- local startup instructions.

VERIFY:
- application starts successfully.
- health endpoint works.
- database connectivity can be verified.
- MinIO connectivity can be verified.
- worker process can start.
- tests execute.
- containers can communicate correctly.

Do not implement business functionality yet.
Do not modify architecture without documenting why.