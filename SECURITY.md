# Security Policy — Fídíò Studio

**Brand:** Fídíò | **Product:** Fídíò Studio  

---

## 1. Security Architecture & Commit Rules

1. **Zero Secret Leakage:** No API keys, passwords, private keys, database connection strings, or JWT secret keys must EVER be committed into source control.
2. **Environment Variable Injection:** All sensitive configuration parameters are managed via `.env` files and loaded into application runtimes using Pydantic `BaseSettings`.
3. **Presigned URL Expiration:** Access to media files stored in MinIO is strictly mediated via temporal presigned URLs (`SIGNED_URL_EXPIRATION_SECONDS=3600`). Raw internal S3 bucket paths or access keys are never exposed to API consumers or frontend clients.
4. **Input Sanitization & Path Traversal Prevention:** Uploaded filenames, MIME types, and prompt strings are sanitized before processing. FFmpeg subprocess executions operate only on validated local paths within `/tmp/fidio_processing` to eliminate command injection risks.
5. **No Media Binaries in Relational Database:** PostgreSQL contains metadata, S3 keys, and job states only. Binary blobs are stored in MinIO.

---

## 2. Vulnerability Reporting

If you discover a potential security vulnerability within Fídíò Studio, please do not open a public issue. Contact the security team at `security@fidio.site`.
