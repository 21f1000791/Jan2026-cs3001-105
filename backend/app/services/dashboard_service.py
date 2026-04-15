from datetime import datetime
from datetime import timedelta

from sqlalchemy import case, extract, func
from sqlalchemy import text

from app.models import Notification, Task, TaskStatusHistory, Translation, User


class DashboardService:
    @staticmethod
    def _scoped_active_tasks(user=None):
        active_tasks = Task.query.filter(text("tasks.is_deleted = 0"))
        manager_categories = []
        scoped_by_manager = False

        if user and getattr(user, "role", None) == "manager":
            scoped_by_manager = True
            manager_categories = user.get_managed_categories()
            if manager_categories:
                active_tasks = active_tasks.filter(Task.category.in_(manager_categories))
            else:
                active_tasks = active_tasks.filter(text("1 = 0"))

        return active_tasks, manager_categories, scoped_by_manager

    @staticmethod
    def _month_window(months=6):
        now = datetime.utcnow()
        labels = []
        cursor = datetime(now.year, now.month, 1)
        for _ in range(months):
            labels.append(cursor.strftime("%Y-%m"))
            if cursor.month == 1:
                cursor = datetime(cursor.year - 1, 12, 1)
            else:
                cursor = datetime(cursor.year, cursor.month - 1, 1)
        labels.reverse()
        return labels

    @staticmethod
    def _month_label(year, month):
        return f"{int(year):04d}-{int(month):02d}"

    @staticmethod
    def _series_from_rows(rows, months=6):
        labels = DashboardService._month_window(months=months)
        value_map = {label: 0 for label in labels}
        for row in rows:
            label = DashboardService._month_label(row.year, row.month)
            if label in value_map:
                value_map[label] = int(row.count or 0)
        return [{"label": label, "value": value_map[label]} for label in labels]

    @staticmethod
    def _labelize_month(label):
        year, month = label.split("-")
        date = datetime(int(year), int(month), 1)
        return date.strftime("%b %Y")

    @staticmethod
    def manager_metrics(user=None):
        active_tasks, manager_categories, scoped_by_manager = DashboardService._scoped_active_tasks(user)

        total = active_tasks.count()
        completed = active_tasks.filter(Task.status == "completed").count()
        overdue = active_tasks.filter(Task.status == "overdue").count()
        pending = active_tasks.filter(Task.status.in_(["todo", "in_progress", "blocked"])).count()
        in_progress = active_tasks.filter(Task.status == "in_progress").count()
        blocked = active_tasks.filter(Task.status == "blocked").count()
        todo = active_tasks.filter(Task.status == "todo").count()

        completion_rate = round((completed / total) * 100, 2) if total else 0.0
        overdue_rate = round((overdue / total) * 100, 2) if total else 0.0

        now = datetime.utcnow()
        due_soon = active_tasks.filter(
            Task.due_date.isnot(None),
            Task.due_date >= now,
            Task.due_date <= now + timedelta(days=3),
            Task.status.in_(["todo", "in_progress", "blocked"]),
        ).count()

        monthly_created_rows = (
            Task.query.with_entities(
                extract("year", Task.created_at).label("year"),
                extract("month", Task.created_at).label("month"),
                func.count(Task.id).label("count"),
            )
            .filter(text("tasks.is_deleted = 0"))
            .filter(Task.category.in_(manager_categories) if scoped_by_manager and manager_categories else text("1 = 1"))
            .filter(text("1 = 0") if scoped_by_manager and not manager_categories else text("1 = 1"))
            .group_by("year", "month")
            .order_by("year", "month")
            .all()
        )

        monthly_completed_rows = (
            TaskStatusHistory.query.with_entities(
                extract("year", TaskStatusHistory.timestamp).label("year"),
                extract("month", TaskStatusHistory.timestamp).label("month"),
                func.count(TaskStatusHistory.id).label("count"),
            )
            .join(Task, Task.id == TaskStatusHistory.task_id)
            .filter(
                text("tasks.is_deleted = 0"),
                TaskStatusHistory.status == "completed",
                Task.category.in_(manager_categories) if scoped_by_manager and manager_categories else text("1 = 1"),
                text("1 = 0") if scoped_by_manager and not manager_categories else text("1 = 1"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
            .all()
        )

        monthly_created = DashboardService._series_from_rows(monthly_created_rows, months=6)
        monthly_completed = DashboardService._series_from_rows(monthly_completed_rows, months=6)

        status_breakdown = [
            {"label": "Completed", "value": completed},
            {"label": "In Progress", "value": in_progress},
            {"label": "Pending", "value": todo},
            {"label": "Blocked", "value": blocked},
            {"label": "Overdue", "value": overdue},
        ]

        priority_rows = (
            active_tasks.with_entities(Task.priority, func.count(Task.id).label("count"))
            .group_by(Task.priority)
            .all()
        )
        priority_breakdown = [
            {"label": str(row.priority).title(), "value": int(row.count or 0)}
            for row in priority_rows
            if row.priority
        ]

        category_rows = (
            active_tasks.with_entities(Task.category, func.count(Task.id).label("count"))
            .group_by(Task.category)
            .order_by(func.count(Task.id).desc())
            .all()
        )
        category_breakdown = [
            {"label": row.category or "Uncategorized", "value": int(row.count or 0)}
            for row in category_rows
        ]

        staff_performance = (
            Task.query.with_entities(
                Task.assigned_to.label("staff_id"),
                User.name.label("staff_name"),
                func.count(Task.id).label("assigned"),
                func.sum(case((Task.status == "completed", 1), else_=0)).label("completed"),
            )
            .join(User, User.id == Task.assigned_to)
            .filter(
                text("tasks.is_deleted = 0"),
                Task.assigned_to.isnot(None),
                Task.category.in_(manager_categories) if scoped_by_manager and manager_categories else text("1 = 1"),
                text("1 = 0") if scoped_by_manager and not manager_categories else text("1 = 1"),
            )
            .group_by(Task.assigned_to, User.name)
            .order_by(func.count(Task.id).desc())
            .all()
        )

        if scoped_by_manager:
            scoped_staff_count = (
                active_tasks.with_entities(func.count(func.distinct(Task.assigned_to)))
                .filter(Task.assigned_to.isnot(None))
                .scalar()
            )
            active_users_by_role = {
                "admin": 0,
                "manager": 1,
                "staff": int(scoped_staff_count or 0),
            }
        else:
            role_counts = (
                User.query.with_entities(User.role, func.count(User.id).label("count"))
                .filter(User.is_active.is_(True))
                .group_by(User.role)
                .all()
            )
            active_users_by_role = {str(row.role): int(row.count or 0) for row in role_counts}

        if scoped_by_manager:
            notifications_total = Notification.query.filter(Notification.user_id == user.id).count()
            notifications_unread = Notification.query.filter(
                Notification.user_id == user.id,
                Notification.is_read.is_(False),
            ).count()
        else:
            notifications_total = Notification.query.count()
            notifications_unread = Notification.query.filter(Notification.is_read.is_(False)).count()

        multilingual_tasks = active_tasks.filter(Task.multilingual_enabled.is_(True)).count()
        expected_translation_rows = multilingual_tasks * 2
        actual_translation_rows = (
            Translation.query.join(Task, Task.id == Translation.task_id)
            .filter(
                text("tasks.is_deleted = 0"),
                Task.multilingual_enabled.is_(True),
                Translation.language.in_(["hi", "kn"]),
                Task.category.in_(manager_categories) if scoped_by_manager and manager_categories else text("1 = 1"),
                text("1 = 0") if scoped_by_manager and not manager_categories else text("1 = 1"),
            )
            .count()
        )
        translation_coverage_pct = (
            round((actual_translation_rows / expected_translation_rows) * 100, 2)
            if expected_translation_rows
            else 100.0
        )

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "completion_rate": completion_rate,
            "overdue_tasks": overdue,
            "overdue_rate": overdue_rate,
            "in_progress_tasks": in_progress,
            "blocked_tasks": blocked,
            "todo_tasks": todo,
            "due_soon_tasks": due_soon,
            "monthly_stats": [
                {
                    "label": DashboardService._labelize_month(point["label"]),
                    "month": int(point["label"].split("-")[1]),
                    "count": int(point["value"]),
                }
                for point in monthly_created
            ],
            "monthly_created": [
                {
                    "label": DashboardService._labelize_month(point["label"]),
                    "value": int(point["value"]),
                }
                for point in monthly_created
            ],
            "monthly_completed": [
                {
                    "label": DashboardService._labelize_month(point["label"]),
                    "value": int(point["value"]),
                }
                for point in monthly_completed
            ],
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "category_breakdown": category_breakdown,
            "staff_performance": [
                {
                    "staff_id": row.staff_id,
                    "staff_name": row.staff_name,
                    "assigned": int(row.assigned),
                    "completed": int(row.completed or 0),
                    "completion_rate": round((int(row.completed or 0) / int(row.assigned)) * 100, 2)
                    if int(row.assigned)
                    else 0.0,
                }
                for row in staff_performance
            ],
            "active_users_by_role": {
                "admin": active_users_by_role.get("admin", 0),
                "manager": active_users_by_role.get("manager", 0),
                "staff": active_users_by_role.get("staff", 0),
            },
            "notifications": {
                "total": notifications_total,
                "unread": notifications_unread,
            },
            "translation_coverage": {
                "multilingual_tasks": multilingual_tasks,
                "expected_rows": expected_translation_rows,
                "actual_rows": actual_translation_rows,
                "coverage_pct": translation_coverage_pct,
            },
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
