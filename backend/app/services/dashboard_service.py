from datetime import datetime

from sqlalchemy import case, extract, func
from sqlalchemy import text

from app.models import Task


class DashboardService:
    @staticmethod
    def manager_metrics():
        total = Task.query.filter(text("tasks.is_deleted = 0")).count()
        completed = Task.query.filter(text("tasks.is_deleted = 0"), Task.status == "completed").count()
        overdue = Task.query.filter(text("tasks.is_deleted = 0"), Task.status == "overdue").count()
        pending = Task.query.filter(
            text("tasks.is_deleted = 0"),
            Task.status.in_(["todo", "in_progress", "blocked"]),
        ).count()

        completion_rate = round((completed / total) * 100, 2) if total else 0.0

        current_year = datetime.utcnow().year
        monthly = (
            Task.query.with_entities(
                extract("month", Task.created_at).label("month"),
                func.count(Task.id).label("count"),
            )
            .filter(text("tasks.is_deleted = 0"), extract("year", Task.created_at) == current_year)
            .group_by("month")
            .order_by("month")
            .all()
        )

        staff_performance = (
            Task.query.with_entities(
                Task.assigned_to.label("staff_id"),
                func.count(Task.id).label("assigned"),
                func.sum(case((Task.status == "completed", 1), else_=0)).label("completed"),
            )
            .filter(text("tasks.is_deleted = 0"), Task.assigned_to.isnot(None))
            .group_by(Task.assigned_to)
            .all()
        )

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": completion_rate,
            "overdue_tasks": overdue,
            "monthly_stats": [{"month": int(row[0]), "count": int(row[1])} for row in monthly],
            "staff_performance": [
                {
                    "staff_id": row.staff_id,
                    "assigned": int(row.assigned),
                    "completed": int(row.completed or 0),
                }
                for row in staff_performance
            ],
        }

    @staticmethod
    def staff_metrics(user_id):
        total = Task.query.filter(text("tasks.is_deleted = 0"), Task.assigned_to == user_id).count()
        completed = Task.query.filter(
            text("tasks.is_deleted = 0"), Task.assigned_to == user_id, Task.status == "completed"
        ).count()
        overdue = Task.query.filter(
            text("tasks.is_deleted = 0"), Task.assigned_to == user_id, Task.status == "overdue"
        ).count()
        pending = Task.query.filter(
            text("tasks.is_deleted = 0"),
            Task.assigned_to == user_id,
            Task.status.in_(["todo", "in_progress", "blocked"]),
        ).count()

        completion_rate = round((completed / total) * 100, 2) if total else 0.0
        return {
            "completion_rate": completion_rate,
            "overdue_tasks": overdue,
            "total_assigned": total,
            "completed": completed,
            "pending_tasks": pending,
        }
