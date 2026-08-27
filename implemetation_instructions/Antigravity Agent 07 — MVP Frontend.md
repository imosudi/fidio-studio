You are the frontend implementation agent.

Read the API contract and architecture before implementation.

Build the MVP web interface.

PRIMARY USER FLOW:

Dashboard
→ New Project
→ Generation Prompt
→ Generation Settings
→ Generate
→ Generation Progress
→ Scene/Asset Review
→ Final Video Preview
→ Download

CORE SCREENS:
1. Dashboard
2. Project list
3. Project detail
4. New generation
5. Generation progress
6. Scene/asset review
7. Final render
8. Basic settings where required

UX REQUIREMENTS:
- Clearly communicate asynchronous job states.
- Show planning/generation/rendering progress.
- Show meaningful errors.
- Prevent duplicate generation submissions.
- Allow retry where supported.
- Handle expired media URLs.
- Show empty/loading/error states.
- Use responsive layout.
- Keep the UI intentionally simple for the MVP.

ARCHITECTURE:
- Separate API client from UI components.
- Separate server/domain data from presentation state.
- Centralise API error handling.
- Centralise authentication/session handling.
- Use typed API contracts where supported.

DO NOT:
- Implement fake generation state once the backend endpoint exists.
- Hard-code example videos into production screens.
- Put business logic into presentation components.
- Couple UI directly to MinIO.

VERIFY USING THE BROWSER:
- project creation
- generation submission
- progress polling/updates
- error state
- final video preview
- download
- refresh/re-entry into an existing project

Create an Antigravity walkthrough artifact documenting the completed user journey and verification results.