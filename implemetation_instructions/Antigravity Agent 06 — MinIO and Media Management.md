You are the media-storage and asset-management agent.

Implement the media abstraction for the MVP.

STORAGE:
MinIO is the primary object store.

Create a provider-independent abstraction:

ObjectStorage
 ├── put
 ├── get
 ├── delete
 ├── exists
 ├── metadata
 └── signed URL generation

Implement:
- MinIO adapter
- bucket initialization
- object naming strategy
- content-type handling
- metadata handling
- signed URLs
- upload/download streaming
- deletion
- existence checks

OBJECT ORGANISATION SHOULD SEPARATE:
- original uploads
- generated images
- generated video clips
- generated audio
- intermediate render files
- final renders
- temporary processing assets

Do not expose raw filesystem paths.

MEDIA VALIDATION:
Implement validation for:
- MIME type
- file size
- video dimensions
- duration
- audio properties where required
- basic corruption/readability checks

FFMPEG:
Create a media utility layer around FFmpeg rather than scattering shell commands through business logic.

The FFmpeg layer should support:
- probing media
- transcoding
- concatenation
- scaling
- aspect-ratio handling
- audio/video muxing
- final rendering

SECURITY:
- Never expose MinIO credentials to clients.
- Validate uploaded media.
- Prevent path traversal.
- Do not trust client-supplied MIME types.

TEST:
Use integration tests against a disposable MinIO instance where practical.