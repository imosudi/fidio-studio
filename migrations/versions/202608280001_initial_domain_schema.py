"""Initial domain schema for Fídíò Studio

Revision ID: 202608280001
Revises: 
Create Date: 2026-08-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '202608280001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # 2. projects
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('aspect_ratio', sa.String(32), server_default='16:9', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('idx_projects_user_id', 'projects', ['user_id'])
    op.create_index('idx_projects_deleted_at', 'projects', ['deleted_at'])

    # 3. generation_requests
    op.create_table(
        'generation_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('style', sa.String(64), server_default='cinematic', nullable=False),
        sa.Column('target_duration_seconds', sa.Integer(), server_default='15', nullable=False),
        sa.Column('aspect_ratio', sa.String(32), server_default='16:9', nullable=False),
        sa.Column('model_config_json', postgresql.JSONB(), nullable=False),
        sa.Column('idempotency_key', sa.String(128), unique=True, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_generation_requests_project_id', 'generation_requests', ['project_id'])
    op.create_index('idx_generation_requests_idempotency_key', 'generation_requests', ['idempotency_key'])

    # 4. generation_plans
    op.create_table(
        'generation_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('generation_request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_requests.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('aspect_ratio', sa.String(32), nullable=False),
        sa.Column('total_estimated_duration_seconds', sa.Float(), nullable=False),
        sa.Column('plan_metadata_json', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 5. scenes
    op.create_table(
        'scenes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('generation_plan_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scene_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('visual_prompt', sa.Text(), nullable=False),
        sa.Column('narration_script', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('transition_type', sa.String(64), server_default='fade', nullable=False),
        sa.Column('camera_movement', sa.String(64), server_default='static', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_scenes_plan_number', 'scenes', ['generation_plan_id', 'scene_number'])

    # 6. generation_jobs
    op.create_table(
        'generation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('generation_request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_requests.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('status', sa.Enum('QUEUED', 'PLANNING', 'GENERATING_ASSETS', 'RENDERING', 'COMPLETED', 'FAILED', 'CANCELLED', name='jobstatus'), nullable=False),
        sa.Column('current_stage', sa.String(64), server_default='INIT', nullable=False),
        sa.Column('progress_percentage', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_code', sa.String(64), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('max_retries', sa.Integer(), server_default='3', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_jobs_status', 'generation_jobs', ['status'])
    op.create_index('idx_jobs_project_status', 'generation_jobs', ['project_id', 'status'])

    # 7. job_steps
    op.create_table(
        'job_steps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('step_name', sa.String(64), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'SKIPPED', name='stepstatus'), nullable=False),
        sa.Column('execution_metadata_json', postgresql.JSONB(), nullable=False),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.create_index('idx_job_steps_job_id', 'job_steps', ['job_id'])

    # 8. media_assets
    op.create_table(
        'media_assets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scene_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('scenes.id', ondelete='SET NULL'), nullable=True),
        sa.Column('asset_type', sa.Enum('IMAGE', 'VIDEO', 'AUDIO', 'VOICE', name='assettype'), nullable=False),
        sa.Column('bucket_name', sa.String(128), nullable=False),
        sa.Column('object_key', sa.String(512), nullable=False),
        sa.Column('mime_type', sa.String(128), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_media_assets_project_id', 'media_assets', ['project_id'])
    op.create_index('idx_media_assets_scene_id', 'media_assets', ['scene_id'])

    # 9. renders
    op.create_table(
        'renders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_jobs.id'), nullable=False, unique=True),
        sa.Column('bucket_name', sa.String(128), nullable=False),
        sa.Column('object_key', sa.String(512), nullable=False),
        sa.Column('format', sa.String(32), server_default='mp4', nullable=False),
        sa.Column('resolution', sa.String(32), server_default='1920x1080', nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_renders_project_id', 'renders', ['project_id'])

    # 10. provider_invocations
    op.create_table(
        'provider_invocations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('generation_jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('provider_name', sa.String(64), nullable=False),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=True),
        sa.Column('response_status_code', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_provider_invocations_job_id', 'provider_invocations', ['job_id'])


def downgrade() -> None:
    op.drop_table('provider_invocations')
    op.drop_table('renders')
    op.drop_table('media_assets')
    op.drop_table('job_steps')
    op.drop_table('generation_jobs')
    op.drop_table('scenes')
    op.drop_table('generation_plans')
    op.drop_table('generation_requests')
    op.drop_table('projects')
    op.drop_table('users')

    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS stepstatus')
    op.execute('DROP TYPE IF EXISTS assettype')
