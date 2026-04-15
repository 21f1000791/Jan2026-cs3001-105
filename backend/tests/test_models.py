from datetime import timedelta

from app.extensions import db
from app.models import Notification, Task, TaskStatusHistory, Translation, User
from app.models.base import utc_now


def test_user_password_hashing(app):
    with app.app_context():
        user = User(name="Asha", email="asha@example.com", role="manager")
        user.set_password("StrongPass123")

        db.session.add(user)
        db.session.commit()

        assert user.password_hash != "StrongPass123"
        assert user.check_password("StrongPass123") is True
        assert user.check_password("wrong") is False


def test_task_relationships_and_translation_unique(app):
    with app.app_context():
        manager = User(name="Manager", email="manager@example.com", role="manager")
        manager.set_password("Password!234")
        staff = User(name="Staff", email="staff@example.com", role="staff")
        staff.set_password("Password!234")

        db.session.add_all([manager, staff])
        db.session.flush()

        task = Task(
            title="Prepare inventory report",
            description="Collect stock data and submit report",
            category="Construction",
            due_date=utc_now() + timedelta(days=2),
            priority="high",
            status="todo",
            assigned_to=staff.id,
            created_by=manager.id,
            multilingual_enabled=True,
        )
        db.session.add(task)
        db.session.flush()

        history = TaskStatusHistory(task_id=task.id, status="todo")
        translation_hi = Translation(
            task_id=task.id,
            language="hi",
            translated_text="इन्वेंटरी रिपोर्ट तैयार करें",
            translated_title="इन्वेंटरी रिपोर्ट तैयार करें",
        )
        translation_kn = Translation(
            task_id=task.id,
            language="kn",
            translated_text="ಇನ್‌ವೆಂಟರಿ ವರದಿ ತಯಾರಿಸಿ",
            translated_title="ಇನ್‌ವೆಂಟರಿ ವರದಿ ತಯಾರಿಸಿ",
        )
        note = Notification(user_id=staff.id, message="A new task was assigned")

        db.session.add_all([history, translation_hi, translation_kn, note])
        db.session.commit()

        assert manager.created_tasks.count() == 1
        assert staff.assigned_tasks.count() == 1
        task_status_history = TaskStatusHistory.query.filter_by(task_id=task.id).all()
        task_translations = Translation.query.filter_by(task_id=task.id).all()

        assert task_status_history[0].status == "todo"
        assert len(task_translations) == 2
        assert staff.notifications.count() == 1


def test_task_soft_delete_and_restore(app):
    with app.app_context():
        manager = User(name="Delete Manager", email="delete.manager@example.com", role="manager")
        manager.set_password("Password!234")
        db.session.add(manager)
        db.session.flush()

        task = Task(
            title="Archive file room",
            description="Mark old files for archive",
            category="Maintenance",
            priority="medium",
            status="todo",
            created_by=manager.id,
        )
        db.session.add(task)
        db.session.commit()

        task.soft_delete()
        db.session.commit()
        assert task.is_deleted is True
        assert task.deleted_at is not None

        task.restore()
        db.session.commit()
        assert task.is_deleted is False
        assert task.deleted_at is None
