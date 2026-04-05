from flask_jwt_extended import create_access_token, decode_token
from sqlalchemy import or_

from app.extensions import db
from app.models import User
from app.models.token_blocklist import TokenBlocklist


class AuthService:
    SYSTEM_ADMIN_NAME = "admin"
    SYSTEM_ADMIN_EMAIL = "admin@gmail.com"
    SYSTEM_ADMIN_PASSWORD = "admin"

    @staticmethod
    def ensure_default_admin():
        # Keep one canonical admin account for this project.
        admin = User.query.filter_by(role="admin").order_by(User.id.asc()).first()
        if admin is None:
            admin = User(
                name=AuthService.SYSTEM_ADMIN_NAME,
                email=AuthService.SYSTEM_ADMIN_EMAIL,
                role="admin",
                is_active=True,
            )
            admin.set_password(AuthService.SYSTEM_ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            return admin

        changed = False
        if admin.name != AuthService.SYSTEM_ADMIN_NAME:
            admin.name = AuthService.SYSTEM_ADMIN_NAME
            changed = True

        desired_email = AuthService.SYSTEM_ADMIN_EMAIL
        email_in_use = User.query.filter(User.email == desired_email, User.id != admin.id).first()
        if admin.email != desired_email and email_in_use is None:
            admin.email = desired_email
            changed = True
        if not admin.is_active:
            admin.is_active = True
            changed = True
        if not admin.check_password(AuthService.SYSTEM_ADMIN_PASSWORD):
            admin.set_password(AuthService.SYSTEM_ADMIN_PASSWORD)
            changed = True

        if changed:
            db.session.commit()

        return admin

    @staticmethod
    def register_user(name: str, email: str, password: str, role: str = "staff"):
        AuthService.ensure_default_admin()

        if role == "admin":
            return None, "Admin account is system-managed."

        existing = User.query.filter_by(email=email).first()
        if existing:
            return None, "Email already exists."

        user = User(name=name, email=email.lower().strip(), role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login_user(identifier: str, password: str):
        admin = AuthService.ensure_default_admin()

        normalized = (identifier or "").strip().lower()

        if normalized in {AuthService.SYSTEM_ADMIN_NAME, AuthService.SYSTEM_ADMIN_EMAIL}:
            user = admin
        else:
            user = User.query.filter(
                or_(User.email == normalized, User.name == normalized)
            ).first()

        if user is None or not user.check_password(password):
            return None, None, "Invalid email or password."
        if not user.is_active:
            return None, None, "User account is inactive."

        token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return user, token, None

    @staticmethod
    def revoke_token(encoded_token: str):
        decoded = decode_token(encoded_token)
        jti = decoded.get("jti")
        if not jti:
            return

        already = TokenBlocklist.query.filter_by(jti=jti).first()
        if already:
            return

        db.session.add(TokenBlocklist(jti=jti))
        db.session.commit()
