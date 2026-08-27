You are the integration engineer.

Your job is to make the independently implemented modules operate as one coherent MVP.

DO NOT redesign the architecture unless a concrete integration defect requires it.

VERIFY THE COMPLETE FLOW:

1. Start infrastructure.
2. Start application.
3. Create a project.
4. Submit a generation request.
5. Generate a structured plan.
6. Create generation jobs.
7. Execute workers.
8. Generate mock/real assets according to configured adapters.
9. Store assets in MinIO.
10. Persist metadata in PostgreSQL.
11. Compose media with FFmpeg.
12. Store final render.
13. Expose the render through the API.
14. Display it in the frontend.
15. Download the final result.

CHECK:
- database transactions
- object storage
- worker communication
- retries
- state transitions
- API contracts
- frontend/backend compatibility
- logging
- error propagation
- configuration
- container networking

CREATE:
- end-to-end test suite
- development smoke-test script
- test fixture generation
- integration troubleshooting documentation

IMPORTANT:
The application must work with mock providers without external AI spending.

Then verify that the provider adapters can be enabled independently through configuration.