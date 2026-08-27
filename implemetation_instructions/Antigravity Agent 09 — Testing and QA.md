You are the senior QA and reliability engineer.

Treat the current repository as an implementation candidate that must be verified rather than assumed correct.

BUILD A TEST MATRIX COVERING:

UNIT:
- domain logic
- state transitions
- prompt planner
- provider adapters
- storage adapter
- media utilities
- retry logic

INTEGRATION:
- PostgreSQL
- MinIO
- API
- worker
- OpenRouter adapter
- FFmpeg

END-TO-END:
- create project
- submit generation
- monitor job
- complete generation
- preview result
- download result

FAILURE TESTS:
- database unavailable
- MinIO unavailable
- provider timeout
- provider rate limit
- malformed model response
- worker crash
- duplicate job delivery
- corrupt media
- FFmpeg failure
- expired object URL
- invalid request
- unauthorized request

PERFORMANCE:
Measure:
- API latency
- job startup latency
- database query performance
- object-storage throughput where practical
- worker concurrency
- memory consumption
- CPU consumption during rendering

DO NOT merely increase timeouts to make tests pass.

Every discovered defect should be:
1. Reproduced.
2. Root-caused.
3. Fixed.
4. Covered by a regression test.

Produce a final QA report as an Antigravity artifact.