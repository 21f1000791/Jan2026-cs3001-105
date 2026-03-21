from app.models import Notification, Task, TaskStatusHistory, Translation, User


def serialize_user(user: User):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def serialize_translation(translation: Translation):
    return {
        "id": translation.id,
        "task_id": translation.task_id,
        "language": translation.language,
        "translated_text": translation.translated_text,
        "created_at": translation.created_at.isoformat() if translation.created_at else None,
        "updated_at": translation.updated_at.isoformat() if translation.updated_at else None,
    }


def serialize_status_history(item: TaskStatusHistory):
    return {
        "id": item.id,
        "task_id": item.task_id,
        "status": item.status,
        "timestamp": item.timestamp.isoformat() if item.timestamp else None,
    }


def serialize_task(task: Task):
    translations = Translation.query.filter_by(task_id=task.id).all()
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "category": task.category,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "status": task.status,
        "assigned_to": task.assigned_to,
        "created_by": task.created_by,
        "multilingual_enabled": task.multilingual_enabled,
        "is_deleted": task.is_deleted,
        "deleted_at": task.deleted_at.isoformat() if task.deleted_at else None,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "translations": [serialize_translation(t) for t in translations],
    }


def serialize_notification(notification: Notification):
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "is_read": notification.is_read,
        "timestamp": notification.timestamp.isoformat() if notification.timestamp else None,
    }
