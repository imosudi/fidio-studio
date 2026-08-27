Act as the principal engineer reviewing the current MVP implementation.

Do not implement new features yet.

Review the repository against:
- AGENTS.md
- architecture documentation
- database model
- API contract
- generation pipeline contract
- storage contract
- frontend flow
- test strategy

CHECK FOR:
1. Architectural violations.
2. Circular dependencies.
3. Provider coupling.
4. Missing error handling.
5. Incorrect asynchronous boundaries.
6. Database transaction problems.
7. Race conditions.
8. Non-idempotent operations.
9. Missing persistence.
10. Object-storage security problems.
11. Secrets leakage.
12. Missing tests.
13. Unnecessary complexity.
14. Inconsistent naming.
15. Dead code.
16. Configuration inconsistencies.
17. Docker networking problems.
18. Broken developer setup.

For every finding provide:
- severity
- location
- explanation
- recommended correction
- whether correction is blocking

Do not make changes unless explicitly requested after the review.

Produce a concise review artifact suitable for handing to the next implementation agent.