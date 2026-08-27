# Database Conventions & Schema Blueprint — Fídíò Studio

**Engine:** PostgreSQL 14+  
**ORM:** SQLAlchemy 2.0 (Async Engine)  
**Migrations:** Alembic  
**Database Name:** `fidio-studio`  

---

## 1. Core Persistence Rules

1. **External PostgreSQL:** PostgreSQL is hosted externally to the Docker application stack. All connection credentials (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) are read via environment variables.
2. **No Binaries in PostgreSQL:** Media assets (images, video clips, voiceovers, final MP4 renders) are stored exclusively in MinIO object storage. PostgreSQL stores only S3 keys (`object_key`), bucket names, mime-types, file sizes, and metadata.
3. **Explicit Primary Keys & UUIDs:** All tables use UUID v4 or ULID primary keys (`id`). Internal sequence numbers are avoided for domain entities.
4. **UTC Timestamps:** All datetime columns store timezone-aware UTC timestamps (`created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `updated_at`).
5. **Soft Deletes:** Key user resources (`Project`) use soft deletion (`deleted_at TIMESTAMPTZ NULL`).

---

## 2. Schema Lifecycle & Migration Conventions

- **Alembic Migrations:** All schema changes must be declared as revision scripts in `migrations/versions/`. Hand-crafted raw DDL runs in production are prohibited.
- **Migration Naming:** Revision script messages must follow `<timestamp>_<short_snake_case_description>.py`.
- **Reversibility:** Every migration MUST supply both `upgrade()` and `downgrade()` procedures.

---

## 3. Entity-Relationship Diagram (Conceptual)

```
[User] 1 ─── N [Project] 1 ─── N [GenerationRequest] 1 ─── 1 [GenerationPlan] 1 ─── N [Scene]
   │               │                                                  │                 │
   │               └─── N [ProjectAsset]                              │                 │
   │                                                                  ▼                 ▼
   └───────────────────────────────────────────────────────── N [GenerationJob]   [MediaAsset]
                                                                      │                 │
                                                                      ├── N [JobStep]   │
                                                                      │                 │
                                                                      └── 1 [Render] ───┘
```

---

## 4. Table Definitions & Domain Attributes

### 4.1 `users`
- `id` UUID PRIMARY KEY
- `email` VARCHAR(255) UNIQUE NOT NULL
- `hashed_password` VARCHAR(255) NOT NULL
- `full_name` VARCHAR(255) NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.2 `projects`
- `id` UUID PRIMARY KEY
- `user_id` UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- `name` VARCHAR(255) NOT NULL
- `description` TEXT NULL
- `aspect_ratio` VARCHAR(32) NOT NULL DEFAULT '16:9'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `deleted_at` TIMESTAMPTZ NULL

### 4.3 `generation_requests`
- `id` UUID PRIMARY KEY
- `project_id` UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE
- `user_id` UUID NOT NULL REFERENCES users(id)
- `prompt` TEXT NOT NULL
- `style` VARCHAR(64) NOT NULL DEFAULT 'cinematic'
- `target_duration_seconds` INT NOT NULL DEFAULT 15
- `aspect_ratio` VARCHAR(32) NOT NULL DEFAULT '16:9'
- `model_config_json` JSONB NOT NULL DEFAULT '{}'::jsonb
- `idempotency_key` VARCHAR(128) UNIQUE NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.4 `generation_plans`
- `id` UUID PRIMARY KEY
- `generation_request_id` UUID NOT NULL REFERENCES generation_requests(id) ON DELETE CASCADE
- `title` VARCHAR(255) NOT NULL
- `summary` TEXT NOT NULL
- `aspect_ratio` VARCHAR(32) NOT NULL
- `total_estimated_duration_seconds` FLOAT NOT NULL
- `plan_metadata_json` JSONB NOT NULL DEFAULT '{}'::jsonb
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.5 `scenes`
- `id` UUID PRIMARY KEY
- `generation_plan_id` UUID NOT NULL REFERENCES generation_plans(id) ON DELETE CASCADE
- `scene_number` INT NOT NULL
- `title` VARCHAR(255) NOT NULL
- `visual_prompt` TEXT NOT NULL
- `narration_script` TEXT NULL
- `duration_seconds` FLOAT NOT NULL
- `transition_type` VARCHAR(64) NOT NULL DEFAULT 'fade'
- `camera_movement` VARCHAR(64) NOT NULL DEFAULT 'static'
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.6 `generation_jobs`
- `id` UUID PRIMARY KEY
- `generation_request_id` UUID NOT NULL REFERENCES generation_requests(id) ON DELETE CASCADE
- `project_id` UUID NOT NULL REFERENCES projects(id)
- `status` VARCHAR(32) NOT NULL DEFAULT 'QUEUED' -- QUEUED, PLANNING, GENERATING_ASSETS, RENDERING, COMPLETED, FAILED, CANCELLED
- `current_stage` VARCHAR(64) NOT NULL DEFAULT 'INIT'
- `progress_percentage` INT NOT NULL DEFAULT 0
- `error_code` VARCHAR(64) NULL
- `error_message` TEXT NULL
- `retry_count` INT NOT NULL DEFAULT 0
- `max_retries` INT NOT NULL DEFAULT 3
- `started_at` TIMESTAMPTZ NULL
- `completed_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.7 `job_steps`
- `id` UUID PRIMARY KEY
- `job_id` UUID NOT NULL REFERENCES generation_jobs(id) ON DELETE CASCADE
- `step_name` VARCHAR(64) NOT NULL -- e.g. llm_planning, scene_1_visual, scene_1_audio, ffmpeg_composition
- `status` VARCHAR(32) NOT NULL DEFAULT 'PENDING'
- `execution_metadata_json` JSONB NOT NULL DEFAULT '{}'::jsonb
- `error_details` TEXT NULL
- `started_at` TIMESTAMPTZ NULL
- `completed_at` TIMESTAMPTZ NULL

### 4.8 `media_assets`
- `id` UUID PRIMARY KEY
- `project_id` UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE
- `scene_id` UUID NULL REFERENCES scenes(id) ON DELETE SET NULL
- `asset_type` VARCHAR(32) NOT NULL -- IMAGE, VIDEO, AUDIO, VOICE
- `bucket_name` VARCHAR(128) NOT NULL
- `object_key` VARCHAR(512) NOT NULL
- `mime_type` VARCHAR(128) NOT NULL
- `file_size_bytes` BIGINT NOT NULL
- `duration_seconds` FLOAT NULL
- `width` INT NULL
- `height` INT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 4.9 `renders`
- `id` UUID PRIMARY KEY
- `project_id` UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE
- `job_id` UUID NOT NULL REFERENCES generation_jobs(id)
- `bucket_name` VARCHAR(128) NOT NULL
- `object_key` VARCHAR(512) NOT NULL
- `format` VARCHAR(32) NOT NULL DEFAULT 'mp4'
- `resolution` VARCHAR(32) NOT NULL DEFAULT '1920x1080'
- `duration_seconds` FLOAT NOT NULL
- `file_size_bytes` BIGINT NOT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

---

## 5. Indexes & Optimization Constraints

- `idx_projects_user_id` ON `projects(user_id)`
- `idx_generation_requests_project_id` ON `generation_requests(project_id)`
- `idx_generation_jobs_status` ON `generation_jobs(status)`
- `idx_generation_jobs_project_id` ON `generation_jobs(project_id)`
- `idx_scenes_plan_id` ON `scenes(generation_plan_id, scene_number)`
- `idx_media_assets_scene_id` ON `media_assets(scene_id)`
- `idx_idempotency_key` ON `generation_requests(idempotency_key)`
