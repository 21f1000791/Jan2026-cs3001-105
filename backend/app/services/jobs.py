from celery.schedules import crontab

from app.services.notification_service import NotificationService


def register_periodic_jobs(celery_app):
    celery_app.conf.beat_schedule = {
        "due-overdue-notification-job": {
            "task": "jobs.generate_due_and_overdue_notifications",
            "schedule": crontab(minute="*/10"),
        }
    }

    @celery_app.task(name="jobs.generate_due_and_overdue_notifications")
    def generate_due_and_overdue_notifications():
        return NotificationService.generate_due_and_overdue_notifications()

    return celery_app
