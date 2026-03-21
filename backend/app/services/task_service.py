from datetime import datetime

from sqlalchemy import or_
from sqlalchemy import text

from app.extensions import db
from app.models import Task, TaskStatusHistory, Translation, User
from app.models.base import utc_now
from app.services.notification_service import NotificationService
from app.services.translation_service import translate_text


class TaskService:
    ALLOWED_PRIORITIES = {"low", "medium", "high", "urgent"}
    ALLOWED_STATUSES = {"todo", "in_progress", "blocked", "completed", "overdue"}

    @staticmethod
    def _normalize_priority(value):
        if value is None:
            return "medium"
        normalized = str(value).strip().lower()
        if normalized not in TaskService.ALLOWED_PRIORITIES:
            return None
        return normalized

    @staticmethod
    def _normalize_status(value):
        if value is None:
            return "todo"
        normalized = str(value).strip().lower().replace(" ", "_")
        if normalized not in TaskService.ALLOWED_STATUSES:
            return None
        return normalized

    @staticmethod
    def _normalize_description_payload(value):
        if isinstance(value, dict):
            en = (value.get("en") or "").strip()
            hi = (value.get("hi") or "").strip()
            kn = (value.get("kn") or "").strip()

            description_text = en or hi or kn or ""
            translations = {"hi": hi, "kn": kn}
            return description_text, translations

        if value is None:
            return None, {}

        return str(value), {}

    @staticmethod
    def _sync_translations(task_id, translations):
        for lang in ["hi", "kn"]:
            text_value = (translations.get(lang) or "").strip()
            existing = Translation.query.filter_by(task_id=task_id, language=lang).first()

            if text_value:
                if existing:
                    existing.translated_text = text_value
                else:
                    db.session.add(
                        Translation(task_id=task_id, language=lang, translated_text=text_value)
                    )
            elif existing:
                db.session.delete(existing)

    @staticmethod
    def _parse_due_date(value):
        if not value:
            return None
        try:
            normalized = value.replace("Z", "+00:00")
            return datetime.fromisoformat(normalized)
        except ValueError:
            return None

    @staticmethod
    def create_task(payload, creator_id):
        title = payload.get("title", "").strip()
        if not title:
            return None, "title is required"

        priority = TaskService._normalize_priority(payload.get("priority", "medium"))
        if priority is None:
            return None, "Invalid priority. Use low, medium, high, or urgent."

        status = TaskService._normalize_status(payload.get("status", "todo"))
        if status is None:
            return None, "Invalid status."

        description_text, description_translations = TaskService._normalize_description_payload(
            payload.get("description")
        )

        assigned_to = payload.get("assigned_to")
        if assigned_to is not None and db.session.get(User, assigned_to) is None:
            return None, "assigned_to user not found"

        multilingual_enabled = bool(payload.get("multilingual_enabled", False))
        if description_translations.get("hi") or description_translations.get("kn"):
            multilingual_enabled = True

        task = Task(
            title=title,
            description=description_text,
            category=payload.get("category"),
            due_date=TaskService._parse_due_date(payload.get("due_date")),
            priority=priority,
            status=status,
            assigned_to=assigned_to,
            created_by=creator_id,
            multilingual_enabled=multilingual_enabled,
        )
        db.session.add(task)
        db.session.flush()

        db.session.add(TaskStatusHistory(task_id=task.id, status=task.status, timestamp=utc_now()))
        NotificationService.notify_task_assignment(task)

        if description_translations:
            TaskService._sync_translations(task.id, description_translations)
        elif task.multilingual_enabled and task.description:
            generated = {
                "hi": translate_text(task.description, "hi"),
                "kn": translate_text(task.description, "kn"),
            }
            TaskService._sync_translations(task.id, generated)

        db.session.commit()
        return task, None

    @staticmethod
    def update_task(task, payload):
        previous_assignee = task.assigned_to

        for key in ["title", "category", "multilingual_enabled"]:
            if key in payload:
                setattr(task, key, payload[key])

        if "priority" in payload:
            normalized_priority = TaskService._normalize_priority(payload.get("priority"))
            if normalized_priority is None:
                return None, "Invalid priority. Use low, medium, high, or urgent."
            task.priority = normalized_priority

        if "status" in payload:
            normalized_status = TaskService._normalize_status(payload.get("status"))
            if normalized_status is None:
                return None, "Invalid status."
            task.status = normalized_status

        description_translations = None
        if "description" in payload:
            description_text, description_translations = TaskService._normalize_description_payload(
                payload.get("description")
            )
            task.description = description_text

            if description_translations and (
                description_translations.get("hi") or description_translations.get("kn")
            ):
                task.multilingual_enabled = True

        if "due_date" in payload:
            task.due_date = TaskService._parse_due_date(payload.get("due_date"))

        if "assigned_to" in payload:
            assigned_to = payload.get("assigned_to")
            if assigned_to is not None and db.session.get(User, assigned_to) is None:
                return None, "assigned_to user not found"
            task.assigned_to = assigned_to

        if "status" in payload:
            db.session.add(TaskStatusHistory(task_id=task.id, status=task.status, timestamp=utc_now()))

        if task.assigned_to != previous_assignee:
            NotificationService.notify_task_assignment(task)

        if description_translations is not None:
            TaskService._sync_translations(task.id, description_translations)
        elif task.multilingual_enabled and task.description and payload.get("regenerate_translations"):
            Translation.query.filter_by(task_id=task.id).delete()
            generated = {
                "hi": translate_text(task.description, "hi"),
                "kn": translate_text(task.description, "kn"),
            }
            TaskService._sync_translations(task.id, generated)

        db.session.commit()
        return task, None

    @staticmethod
    def list_tasks(filters, include_deleted=False):
        query = Task.query
        if not include_deleted:
            query = query.filter(text("tasks.is_deleted = 0"))

        if filters.get("status"):
            query = query.filter(Task.status == filters["status"])
        if filters.get("category"):
            query = query.filter(Task.category == filters["category"])
        if filters.get("date"):
            parsed = TaskService._parse_due_date(filters["date"])
            if parsed:
                query = query.filter(Task.due_date >= parsed)
        if filters.get("q"):
            q = f"%{filters['q']}%"
            query = query.filter(or_(Task.title.ilike(q), Task.description.ilike(q), Task.category.ilike(q)))

        return query.order_by(Task.created_at.desc())

    @staticmethod
    def set_task_status(task, new_status):
        task.status = new_status
        db.session.add(TaskStatusHistory(task_id=task.id, status=new_status, timestamp=utc_now()))
        db.session.commit()
        return task
