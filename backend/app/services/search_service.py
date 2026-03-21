from sqlalchemy import or_

from app.models import Task


class SearchService:
    @staticmethod
    def search_tasks(query_text, include_deleted=False):
        query = Task.query
        if not include_deleted:
            query = query.filter(Task.is_deleted.is_(False))

        if not query_text:
            return query.order_by(Task.created_at.desc())

        pattern = f"%{query_text}%"
        return query.filter(
            or_(
                Task.title.ilike(pattern),
                Task.description.ilike(pattern),
                Task.category.ilike(pattern),
            )
        ).order_by(Task.created_at.desc())
