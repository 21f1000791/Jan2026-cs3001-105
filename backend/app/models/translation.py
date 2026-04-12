from app.extensions import db
from app.models.base import TimestampMixin


class Translation(TimestampMixin, db.Model):
    __tablename__ = "translations"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    language = db.Column(db.String(20), nullable=False, index=True)
    translated_text = db.Column(db.Text, nullable=False)
    translated_title = db.Column(db.Text, nullable=False)
    

    task = db.relationship("Task", back_populates="translations")

    __table_args__ = (
        db.UniqueConstraint("task_id", "language", name="uq_translations_task_language"),
        db.CheckConstraint("language IN ('en', 'hi', 'kn')", name="ck_translations_language"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Translation task_id={self.task_id} language={self.language}>"
