from flask import request
from flask_restful import Resource

from app.extensions import db
from app.middleware.authz import get_current_user, role_required
from app.models import User
from app.utils.serializers import serialize_user


class MeResource(Resource):
    method_decorators = [role_required("manager", "staff", "admin")]

    def get(self):
        return {"user": serialize_user(get_current_user())}, 200


class UserListResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def get(self):
        users = User.query.order_by(User.created_at.desc()).all()
        return {"items": [serialize_user(u) for u in users]}, 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        role = (payload.get("role") or "staff").strip().lower()

        if not name or not email or not password:
            return {"message": "name, email and password are required."}, 400
        if role not in {"manager", "staff", "admin"}:
            return {"message": "Invalid role."}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists."}, 409

        user = User(name=name, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created.", "user": serialize_user(user)}, 201


class UserDetailResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        payload = request.get_json(silent=True) or {}

        if "name" in payload:
            user.name = (payload.get("name") or "").strip() or user.name

        if "email" in payload:
            next_email = (payload.get("email") or "").strip().lower()
            if not next_email:
                return {"message": "email cannot be empty."}, 400
            existing = User.query.filter(User.email == next_email, User.id != user.id).first()
            if existing:
                return {"message": "Email already exists."}, 409
            user.email = next_email

        if "role" in payload:
            role = (payload.get("role") or "").strip().lower()
            if role not in {"manager", "staff", "admin"}:
                return {"message": "Invalid role."}, 400
            user.role = role

        if "password" in payload and payload.get("password"):
            user.set_password(payload["password"])

        if "is_active" in payload:
            user.is_active = bool(payload.get("is_active"))

        db.session.commit()
        return {"message": "User updated.", "user": serialize_user(user)}, 200

    def patch(self, user_id):
        return self.put(user_id)


class UserTerminateResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = False
        db.session.commit()
        return {"message": "User deactivated.", "user": serialize_user(user)}, 200


class UserActivateResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        user.is_active = True
        db.session.commit()
        return {"message": "User activated.", "user": serialize_user(user)}, 200


class UserHardDeleteResource(Resource):
    method_decorators = [role_required("admin")]

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        current = get_current_user()
        if current and current.id == user.id:
            return {"message": "Cannot hard-delete your own account."}, 400

        db.session.delete(user)
        db.session.commit()
        return {"message": "User permanently deleted."}, 200


def register_resources(api):
    api.add_resource(MeResource, "/users/me")
    api.add_resource(UserListResource, "/users")
    api.add_resource(UserDetailResource, "/users/<int:user_id>")
    api.add_resource(UserTerminateResource, "/users/<int:user_id>/terminate")
    api.add_resource(UserActivateResource, "/users/<int:user_id>/activate")
    api.add_resource(UserHardDeleteResource, "/users/<int:user_id>/hard")
