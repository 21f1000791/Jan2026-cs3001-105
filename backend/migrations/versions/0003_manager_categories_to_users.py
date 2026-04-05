"""move manager categories to users

Revision ID: 0003_manager_categories_to_users
Revises: 0002_manager_category_assignments
Create Date: 2026-03-30 00:00:00
"""

from alembic import op
import sqlalchemy as sa
import json

# revision identifiers, used by Alembic.
revision = "0003_manager_categories_to_users"
down_revision = "0002_manager_category_assignments"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("managed_categories", sa.Text(), nullable=False, server_default="[]"))

    conn = op.get_bind()
    rows = conn.execute(
        sa.text(
            """
            SELECT manager_id, category
            FROM manager_category_assignments
            ORDER BY manager_id, category
            """
        )
    ).fetchall()

    by_manager = {}
    for manager_id, category in rows:
        by_manager.setdefault(manager_id, [])
        if category and category not in by_manager[manager_id]:
            by_manager[manager_id].append(category)

    for manager_id, categories in by_manager.items():
        json_value = json.dumps(categories)
        conn.execute(
            sa.text(
                """
                UPDATE users
                SET managed_categories = :managed_categories
                WHERE id = :manager_id
                """
            ),
            {"managed_categories": json_value, "manager_id": manager_id},
        )

    op.drop_index(op.f("ix_manager_category_assignments_manager_id"), table_name="manager_category_assignments")
    op.drop_index(op.f("ix_manager_category_assignments_category"), table_name="manager_category_assignments")
    op.drop_table("manager_category_assignments")


def downgrade():
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

    op.drop_column("users", "managed_categories")