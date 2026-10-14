"""Persistent workflow operations, isolated from chain/wallet state."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
revision = "087_workflow_operations"
down_revision = "086_acp_explorer_index"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("workflow_projects", sa.Column("id", UUID(), primary_key=True), sa.Column("owner_user_id", UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("context_json", JSONB(), nullable=False), sa.Column("retention_days", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_workflow_projects_owner_user_id", "workflow_projects", ["owner_user_id"])
    op.add_column("workflow_projects", sa.Column("members_json", JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")))
    op.create_table("workflow_connections", sa.Column("id", UUID(), primary_key=True), sa.Column("owner_user_id", UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("kind", sa.String(24), nullable=False), sa.Column("config_json", JSONB(), nullable=False), sa.Column("secret_box", sa.Text(), nullable=False), sa.Column("allow_delivery", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_workflow_connections_owner_user_id", "workflow_connections", ["owner_user_id"])
    op.create_table("workflow_automations", sa.Column("id", UUID(), primary_key=True), sa.Column("owner_user_id", UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("project_id", UUID(), sa.ForeignKey("workflow_projects.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("versions_json", JSONB(), nullable=False), sa.Column("published_version", sa.Integer()), sa.Column("enabled", sa.Boolean(), nullable=False), sa.Column("interval_minutes", sa.Integer(), nullable=False), sa.Column("monthly_budget_acp", sa.Numeric(36,18), nullable=False), sa.Column("spent_acp", sa.Numeric(36,18), nullable=False), sa.Column("budget_month", sa.String(7)), sa.Column("next_run_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_workflow_automations_owner_user_id", "workflow_automations", ["owner_user_id"])
    op.create_index("ix_workflow_automations_next_run_at", "workflow_automations", ["next_run_at"])
    op.create_table("workflow_operation_runs", sa.Column("id", UUID(), primary_key=True), sa.Column("owner_user_id", UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("automation_id", UUID(), sa.ForeignKey("workflow_automations.id", ondelete="SET NULL")), sa.Column("request_key", sa.String(100), nullable=False), sa.Column("request_hash", sa.String(64), nullable=False), sa.Column("kind", sa.String(16), nullable=False), sa.Column("state", sa.String(24), nullable=False), sa.Column("snapshot_json", JSONB(), nullable=False), sa.Column("progress_json", JSONB(), nullable=False), sa.Column("cost_acp", sa.Numeric(36,18), nullable=False), sa.Column("max_cost_acp", sa.Numeric(36,18), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True)))
    op.create_index("ix_workflow_operation_runs_owner_user_id", "workflow_operation_runs", ["owner_user_id"])
    op.create_index("ix_workflow_operation_runs_state", "workflow_operation_runs", ["state"])
    op.create_index("uq_workflow_ops_owner_request", "workflow_operation_runs", ["owner_user_id", "request_key"], unique=True)

def downgrade():
    for table in ["workflow_operation_runs", "workflow_automations", "workflow_connections", "workflow_projects"]:
        op.drop_table(table)
