You are the release engineer.

The objective is to make the MVP reproducible by a new developer.

AUDIT THE ENTIRE REPOSITORY.

CREATE/UPDATE:

1. README.md
2. Architecture documentation
3. API documentation
4. Environment variable reference
5. Docker deployment instructions
6. Development setup
7. Testing instructions
8. Database migration instructions
9. MinIO setup instructions
10. OpenRouter configuration instructions
11. Worker configuration
12. Troubleshooting guide
13. MVP limitations
14. Known technical debt
15. Future extraction candidates for microservices

PROVIDE CLEAR COMMANDS FOR:

- installing prerequisites
- configuring environment
- starting infrastructure
- starting the application
- running migrations
- running tests
- running linting
- running the worker
- inspecting logs
- stopping the environment
- resetting development data

VERIFY THE DOCUMENTATION FROM A CLEAN DEVELOPMENT ENVIRONMENT IF POSSIBLE.

IMPORTANT:
Do not document commands that do not actually work.

The final repository should allow a competent developer to clone the project, configure environment variables, start the stack, execute migrations, run the application, and complete the basic generation flow without relying on undocumented knowledge.