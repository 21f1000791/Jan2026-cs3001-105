from app.extensions import db
from app.models.base import utc_now


class TaskStatusHistory(db.Model):
    __tablename__ = "task_status_history"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    task = db.relationship("Task", back_populates="status_history")

    __table_args__ = (
        db.CheckConstraint("status IN ('todo', 'in_progress', 'blocked', 'completed', 'overdue')", name="ck_task_status_history_status"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<TaskStatusHistory task_id={self.task_id} status={self.status}>"
