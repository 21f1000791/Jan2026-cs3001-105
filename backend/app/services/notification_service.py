from datetime import timedelta

from sqlalchemy import text

from app.extensions import db
from app.models import Notification, Task
from app.models.base import utc_now


class NotificationService:
    @staticmethod
    def create_notification(user_id: int, message: str):
        notification = Notification(user_id=user_id, message=message)
        db.session.add(notification)
        return notification

    @staticmethod
    def notify_task_assignment(task: Task):
        if task.assigned_to:
            NotificationService.create_notification(
                user_id=task.assigned_to,
                message=f"You have been assigned task '{task.title}'.",
            )

    @staticmethod
    def find_due_soon_tasks(within_minutes=60):
        now = utc_now()
        threshold = now.replace(second=0, microsecond=0)
        upper = threshold + timedelta(minutes=within_minutes)
        return Task.query.filter(
            text("tasks.is_deleted = 0"),
            Task.due_date.isnot(None),
            Task.status.in_(["todo", "in_progress", "blocked"]),
            Task.due_date >= threshold,
            Task.due_date <= upper,
        ).all()

    @staticmethod
    def find_overdue_tasks():
        now = utc_now()
        return Task.query.filter(
            text("tasks.is_deleted = 0"),
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status.in_(["todo", "in_progress", "blocked"]),
        ).all()

    @staticmethod
    def generate_due_and_overdue_notifications():
        due_soon = NotificationService.find_due_soon_tasks(within_minutes=90)
        overdue = NotificationService.find_overdue_tasks()

        due_count = 0
        overdue_count = 0

        for task in due_soon:
            if task.assigned_to:
                NotificationService.create_notification(
                    task.assigned_to,
                    f"Reminder: task '{task.title}' is due soon.",
                )
                due_count += 1

        for task in overdue:
            if task.assigned_to:
                NotificationService.create_notification(
                    task.assigned_to,
                    f"Overdue: task '{task.title}' is past due.",
                )
                overdue_count += 1
            task.status = "overdue"

        db.session.commit()
        return {"due_reminders": due_count, "overdue_notifications": overdue_count}
