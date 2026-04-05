"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-03-18 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "token_blocklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index(op.f("ix_token_blocklist_jti"), "token_blocklist", ["jti"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('manager', 'staff', 'admin')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("multilingual_enabled", sa.Boolean(), nullable=False),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="ck_tasks_priority"),
        sa.CheckConstraint("status IN ('todo', 'in_progress', 'blocked', 'completed', 'overdue')", name="ck_tasks_status"),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_assigned_to"), "tasks", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_tasks_category"), "tasks", ["category"], unique=False)
    op.create_index(op.f("ix_tasks_created_by"), "tasks", ["created_by"], unique=False)
    op.create_index(op.f("ix_tasks_due_date"), "tasks", ["due_date"], unique=False)
    op.create_index(op.f("ix_tasks_is_deleted"), "tasks", ["is_deleted"], unique=False)
    op.create_index(op.f("ix_tasks_priority"), "tasks", ["priority"], unique=False)
    op.create_index(op.f("ix_tasks_status"), "tasks", ["status"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_is_read"), "notifications", ["is_read"], unique=False)
    op.create_index(op.f("ix_notifications_timestamp"), "notifications", ["timestamp"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "task_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('todo', 'in_progress', 'blocked', 'completed', 'overdue')", name="ck_task_status_history_status"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_task_status_history_status"), "task_status_history", ["status"], unique=False)
    op.create_index(op.f("ix_task_status_history_task_id"), "task_status_history", ["task_id"], unique=False)
    op.create_index(op.f("ix_task_status_history_timestamp"), "task_status_history", ["timestamp"], unique=False)

    op.create_table(
        "translations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("translated_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("language IN ('en', 'hi', 'kn')", name="ck_translations_language"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "language", name="uq_translations_task_language"),
    )
    op.create_index(op.f("ix_translations_language"), "translations", ["language"], unique=False)
    op.create_index(op.f("ix_translations_task_id"), "translations", ["task_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_translations_task_id"), table_name="translations")
    op.drop_index(op.f("ix_translations_language"), table_name="translations")
    op.drop_table("translations")

    op.drop_index(op.f("ix_task_status_history_timestamp"), table_name="task_status_history")
    op.drop_index(op.f("ix_task_status_history_task_id"), table_name="task_status_history")
    op.drop_index(op.f("ix_task_status_history_status"), table_name="task_status_history")
    op.drop_table("task_status_history")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_timestamp"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_is_read"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_tasks_status"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_priority"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_is_deleted"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_due_date"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_created_by"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_category"), table_name="tasks")
    op.drop_index(op.f("ix_tasks_assigned_to"), table_name="tasks")
    op.drop_table("tasks")

    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_token_blocklist_jti"), table_name="token_blocklist")
    op.drop_table("token_blocklist")
