"""manager category assignments

Revision ID: 0002_manager_category_assignments
Revises: 0001_initial_schema
Create Date: 2026-03-30 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_manager_category_assignments"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "manager_category_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("manager_id", "category", name="uq_manager_category_assignment"),
    )
    op.create_index(
        op.f("ix_manager_category_assignments_category"),
        "manager_category_assignments",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_manager_category_assignments_manager_id"),
        "manager_category_assignments",
        ["manager_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_manager_category_assignments_manager_id"), table_name="manager_category_assignments")
    op.drop_index(op.f("ix_manager_category_assignments_category"), table_name="manager_category_assignments")
    op.drop_table("manager_category_assignments")
