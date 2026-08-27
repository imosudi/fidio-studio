You are the application-security engineer.

Audit and harden the MVP without changing its fundamental architecture.

CHECK:

SECRETS:
- API keys
- database credentials
- MinIO credentials
- signing keys
- session secrets

API:
- input validation
- authorization
- authentication
- request-size limits
- rate limiting where appropriate
- error disclosure
- CORS
- security headers

STORAGE:
- object access control
- signed URL lifetime
- upload validation
- content-type validation
- path traversal
- unsafe filenames
- object ownership

MEDIA:
- untrusted media processing
- FFmpeg invocation safety
- command injection
- resource exhaustion
- oversized files
- decompression/resource abuse

WORKERS:
- job authorization
- duplicate execution
- malicious job parameters
- resource limits
- timeout enforcement

CONTAINERS:
- non-root execution where practical
- minimal images
- unnecessary capabilities
- secret handling
- exposed ports
- filesystem permissions

DEPENDENCIES:
- dependency vulnerability scan
- outdated packages
- insecure configuration

LOGGING:
Ensure secrets and sensitive tokens never appear in logs.

For every finding:
- classify severity
- explain impact
- fix it where appropriate
- add a regression test when practical

Do not claim the application is secure merely because the tests pass.
Produce a security review artifact with remaining risks explicitly listed.