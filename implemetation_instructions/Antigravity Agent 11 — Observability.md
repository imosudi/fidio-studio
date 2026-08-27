You are the observability engineer.

Implement MVP-level observability without introducing unnecessary infrastructure.

REQUIRED:
- structured application logs
- request correlation IDs
- job IDs in all generation-related logs
- pipeline-stage identifiers
- provider invocation metadata
- generation duration metrics
- job success/failure metrics
- retry counts
- render duration
- storage operation failures

LOG EVENTS SHOULD MAKE IT POSSIBLE TO TRACE:

API request
→ generation job
→ planner invocation
→ provider invocation
→ asset creation
→ render
→ final object
→ completed job

NEVER LOG:
- API keys
- authentication tokens
- signed URLs
- passwords
- unnecessary user secrets

Provide:
- local log format
- troubleshooting guide
- useful health/readiness checks
- basic metrics endpoint if appropriate to the architecture

Keep the observability stack lightweight for the MVP.