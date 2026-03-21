from passlib.context import CryptContext

from app.extensions import db
from app.models.base import TimestampMixin

# bcrypt 5.x can cause runtime compatibility issues with older passlib flows.
# pbkdf2_sha256 is stable, secure, and avoids backend-specific bcrypt errors.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff", index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    created_tasks = db.relationship(
        "Task",
        back_populates="creator",
        foreign_keys="Task.created_by",
        lazy="dynamic",
    )
    assigned_tasks = db.relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assigned_to",
        lazy="dynamic",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    __table_args__ = (
        db.CheckConstraint("role IN ('manager', 'staff', 'admin')", name="ck_users_role"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password: str):
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
