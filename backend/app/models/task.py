from app.extensions import db
from app.models.base import SoftDeleteMixin, TimestampMixin, utc_now


class Task(SoftDeleteMixin, TimestampMixin, db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    due_date = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    priority = db.Column(db.String(20), nullable=False, default="medium", index=True)
    status = db.Column(db.String(20), nullable=False, default="todo", index=True)
    multilingual_enabled = db.Column(db.Boolean, nullable=False, default=False)

    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    creator = db.relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    assignee = db.relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])
    status_history = db.relationship(
        "TaskStatusHistory",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskStatusHistory.timestamp.desc()",
    )
    translations = db.relationship(
        "Translation",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name="ck_tasks_priority"),
        db.CheckConstraint("status IN ('todo', 'in_progress', 'blocked', 'completed', 'overdue')", name="ck_tasks_status"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_status_history(self, status: str):
        history = TaskStatusHistory(task_id=self.id, status=status, timestamp=utc_now())
        db.session.add(history)
        return history

    def __repr__(self):
        return f"<Task id={self.id} title={self.title} status={self.status}>"


from app.models.task_status_history import TaskStatusHistory
