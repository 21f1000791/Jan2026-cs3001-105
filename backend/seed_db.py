"""Idempotent database seeding for Community Operations Platform backend.

Usage:
  python seed_db.py
  python seed_db.py --wipe
"""

import argparse
import os

from sqlalchemy import inspect

from app import create_app
from app.constants.categories import DEFAULT_TASK_CATEGORIES
from app.extensions import db
from app.models import Notification, Task, TaskStatusHistory, Translation, User
from app.models.base import utc_now


SEED_USERS = [
    {
        "name": "Admin User",
        "email": "admin@communityops.local",
        "password": "password123",
        "role": "admin",
    },
    {
        "name": "Manager One",
        "email": "manager@communityops.local",
        "password": "password123",
        "role": "manager",
    },
    {
        "name": "Staff One",
        "email": "staff.one@communityops.local",
        "password": "password123",
        "role": "staff",
    },
    {
        "name": "Staff Two",
        "email": "staff.two@communityops.local",
        "password": "password123",
        "role": "staff",
    },
]

SEED_TASKS = [
    {
        "title": "Prepare weekly operations report",
        "description": "Compile weekly metrics and submit by EOD Friday.",
        "category": "Construction",
        "priority": "high",
        "status": "in_progress",
        "assigned_to": "staff.one@communityops.local",
        "created_by": "manager@communityops.local",
        "multilingual_enabled": True,
        "translations": {
            "hi": "साप्ताहिक मेट्रिक्स संकलित करें और शुक्रवार तक जमा करें।",
            "kn": "ವಾರಾಂತ್ಯ ಮೆಟ್ರಿಕ್‌ಗಳನ್ನು ಸಂಗ್ರಹಿಸಿ ಶುಕ್ರವಾರದೊಳಗೆ ಸಲ್ಲಿಸಿ.",
        },
    },
    {
        "title": "Verify backup health",
        "description": "Run backup verification checklist for production data.",
        "category": "Maintenance",
        "priority": "medium",
        "status": "todo",
        "assigned_to": "staff.two@communityops.local",
        "created_by": "manager@communityops.local",
        "multilingual_enabled": False,
        "translations": {},
    },
]

SEED_NOTIFICATIONS = [
    {
        "email": "staff.one@communityops.local",
        "message": "You have been assigned: Prepare weekly operations report",
    },
    {
        "email": "staff.two@communityops.local",
        "message": "You have been assigned: Verify backup health",
    },
]

SEED_MANAGER_CATEGORIES = {
    "manager@communityops.local": ["Maintenance", "Construction"],
}


def upsert_user(item):
    user = User.query.filter_by(email=item["email"]).first()
    created = False

    if user is None:
        user = User(email=item["email"])
        db.session.add(user)
        created = True

    user.name = item["name"]
    user.role = item["role"]
    user.is_active = True
    user.set_password(item["password"])

    return user, created


def upsert_task(item, users_by_email):
    creator = users_by_email[item["created_by"]]
    assignee = users_by_email[item["assigned_to"]]

    task = Task.query.filter_by(title=item["title"], created_by=creator.id).first()
    created = False

    if task is None:
        task = Task(title=item["title"], created_by=creator.id)
        db.session.add(task)
        db.session.flush()
        created = True

    task.description = item["description"]
    task.category = item["category"]
    task.priority = item["priority"]
    task.status = item["status"]
    task.assigned_to = assignee.id
    task.multilingual_enabled = bool(item.get("multilingual_enabled", False))
    task.is_deleted = False
    task.deleted_at = None

    if created:
        db.session.add(TaskStatusHistory(task_id=task.id, status=task.status, timestamp=utc_now()))

    translations = item.get("translations", {})
    for lang in ["hi", "kn"]:
        text_value = (translations.get(lang) or "").strip()
        existing = Translation.query.filter_by(task_id=task.id, language=lang).first()
        if text_value:
            if existing:
                existing.translated_text = text_value
            else:
                db.session.add(
                    Translation(task_id=task.id, language=lang, translated_text=text_value)
                )
        elif existing:
            db.session.delete(existing)

    return task, created


def upsert_notification(item, users_by_email):
    user = users_by_email[item["email"]]
    existing = Notification.query.filter_by(user_id=user.id, message=item["message"]).first()
    if existing:
        return existing, False

    notification = Notification(user_id=user.id, message=item["message"], is_read=False)
    db.session.add(notification)
    return notification, True


def set_manager_categories(users_by_email):
    for email, categories in SEED_MANAGER_CATEGORIES.items():
        manager = users_by_email.get(email)
        if manager is None or manager.role != "manager":
            continue

        normalized = []
        for category in categories:
            if category not in DEFAULT_TASK_CATEGORIES:
                continue
            if category not in normalized:
                normalized.append(category)

        manager.set_managed_categories(normalized)
        db.session.add(manager)


def wipe_database():
    # Delete child tables first to satisfy FK constraints.
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())

    if "translations" in tables:
        Translation.query.delete()
    if "task_status_history" in tables:
        TaskStatusHistory.query.delete()
    if "notifications" in tables:
        Notification.query.delete()
    if "tasks" in tables:
        Task.query.delete()
    if "users" in tables:
        User.query.delete()

    db.session.commit()


def reset_database_file():
    database_uri = db.engine.url
    if database_uri.get_backend_name() != "sqlite":
        return False

    db_path = database_uri.database
    if not db_path:
        return False

    db.session.remove()
    db.engine.dispose()

    if os.path.exists(db_path):
        os.remove(db_path)
        return True

    return False


def run_seed(wipe=False, reset_db=False):
    if reset_db:
        removed = reset_database_file()
        print(f"database_reset={'yes' if removed else 'no'}")

    # Ensure latest tables exist (including newly added models).
    db.create_all()

    if wipe:
        wipe_database()
        # Recreate after wipe in case full cleanup happened.
        db.create_all()

    created_users = 0
    created_tasks = 0
    created_notifications = 0

    users_by_email = {}
    for item in SEED_USERS:
        user, created = upsert_user(item)
        users_by_email[item["email"]] = user
        if created:
            created_users += 1

    db.session.flush()

    for item in SEED_TASKS:
        _, created = upsert_task(item, users_by_email)
        if created:
            created_tasks += 1

    set_manager_categories(users_by_email)

    for item in SEED_NOTIFICATIONS:
        _, created = upsert_notification(item, users_by_email)
        if created:
            created_notifications += 1

    db.session.commit()

    print("Seed completed")
    print(f"users_created={created_users}")
    print(f"tasks_created={created_tasks}")
    print(f"notifications_created={created_notifications}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Community Operations Platform database")
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Delete all existing users/tasks/notifications before seeding",
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Delete SQLite DB file and recreate schema before seeding",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        run_seed(wipe=args.wipe, reset_db=args.reset_db)
