"""Initial schema creation."""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'workers',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('role', sa.String(64), nullable=False),
        sa.Column('model', sa.String(128), nullable=True),
        sa.Column('status', sa.String(16), default='active'),
        sa.Column('max_tasks', sa.Integer, default=3),
        sa.Column('current_tasks', sa.Integer, default=0),
        sa.Column('total_completed', sa.Integer, default=0),
        sa.Column('last_active', sa.DateTime, nullable=True),
        sa.Column('config', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('title', sa.String(256), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.String(16), default='pending'),
        sa.Column('priority', sa.Integer, default=5),
        sa.Column('worker_id', sa.String(64), sa.ForeignKey('workers.id'), nullable=True),
        sa.Column('parent_task_id', sa.String(64), sa.ForeignKey('tasks.id'), nullable=True),
        sa.Column('progress', sa.Float, default=0.0),
        sa.Column('result', sa.Text, nullable=True),
        sa.Column('metadata_json', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'cron_jobs',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('schedule', sa.String(64), nullable=False),
        sa.Column('prompt', sa.Text, nullable=False),
        sa.Column('enabled', sa.Boolean, default=True),
        sa.Column('worker_id', sa.String(64), sa.ForeignKey('workers.id'), nullable=True),
        sa.Column('last_run', sa.DateTime, nullable=True),
        sa.Column('next_run', sa.DateTime, nullable=True),
        sa.Column('run_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
    )

    op.create_table(
        'workspace_files',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('worker_id', sa.String(64), nullable=False),
        sa.Column('path', sa.String(512), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
    )

    op.create_table(
        'memory',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('worker_id', sa.String(64), nullable=False),
        sa.Column('key', sa.String(128), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('importance', sa.Float, default=1.0),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow),
    )


def downgrade() -> None:
    op.drop_table('memory')
    op.drop_table('workspace_files')
    op.drop_table('cron_jobs')
    op.drop_table('tasks')
    op.drop_table('workers')
