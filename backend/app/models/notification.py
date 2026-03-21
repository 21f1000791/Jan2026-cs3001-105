from app.extensions import db
from app.models.base import utc_now


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    user = db.relationship("User", back_populates="notifications")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Notification id={self.id} user_id={self.user_id} is_read={self.is_read}>"
