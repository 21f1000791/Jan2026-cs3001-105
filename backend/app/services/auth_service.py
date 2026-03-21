from flask_jwt_extended import create_access_token, decode_token

from app.extensions import db
from app.models import User
from app.models.token_blocklist import TokenBlocklist


class AuthService:
    @staticmethod
    def register_user(name: str, email: str, password: str, role: str = "staff"):
        existing = User.query.filter_by(email=email).first()
        if existing:
            return None, "Email already exists."

        user = User(name=name, email=email.lower().strip(), role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login_user(email: str, password: str):
        user = User.query.filter_by(email=email.lower().strip()).first()
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
