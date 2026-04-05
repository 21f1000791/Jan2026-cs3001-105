from flask import request
from flask_restful import Resource

from app.constants.categories import DEFAULT_TASK_CATEGORIES, normalize_category
from app.extensions import db
from app.middleware.authz import get_current_user, role_required
from app.models import User
from app.services.task_service import TaskService
from app.utils.serializers import serialize_user


class MeResource(Resource):
    method_decorators = [role_required("manager", "staff", "admin")]

    def get(self):
        return {"user": serialize_user(get_current_user())}, 200


class UserListResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def get(self):
        current = get_current_user()
        query = User.query
        if current.role == "manager":
            query = query.filter(User.role == "staff")

        users = query.order_by(User.created_at.desc()).all()
        return {"items": [serialize_user(u) for u in users]}, 200

    def post(self):
        current = get_current_user()
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = payload.get("password") or ""
        role = (payload.get("role") or "staff").strip().lower()

        if not name or not email or not password:
            return {"message": "name, email and password are required."}, 400
        if role not in {"manager", "staff", "admin"}:
            return {"message": "Invalid role."}, 400
        if role == "admin":
            return {"message": "Admin account is system-managed."}, 403
        if current.role == "manager" and role != "staff":
            return {"message": "Managers can create only staff users."}, 403

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
        current = get_current_user()
        user = User.query.get_or_404(user_id)
        payload = request.get_json(silent=True) or {}

        if current.role == "manager" and user.role != "staff":
            return {"message": "Managers can edit only staff users."}, 403
        if user.role == "admin":
            return {"message": "Admin account is system-managed and cannot be edited."}, 403

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
            if role == "admin":
                return {"message": "Admin account is system-managed."}, 403
            if current.role == "manager" and role != "staff":
                return {"message": "Managers cannot change roles beyond staff."}, 403
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
        current = get_current_user()
        user = User.query.get_or_404(user_id)
        if user.role == "admin":
            return {"message": "Admin account cannot be deactivated."}, 403
        if current.role == "manager" and user.role != "staff":
            return {"message": "Managers can deactivate only staff users."}, 403

        user.is_active = False
        db.session.commit()
        return {"message": "User deactivated.", "user": serialize_user(user)}, 200


class UserActivateResource(Resource):
    method_decorators = [role_required("manager", "admin")]

    def put(self, user_id):
        current = get_current_user()
        user = User.query.get_or_404(user_id)
        if user.role == "admin":
            return {"message": "Admin account is always active."}, 403
        if current.role == "manager" and user.role != "staff":
            return {"message": "Managers can activate only staff users."}, 403

        user.is_active = True
        db.session.commit()
        return {"message": "User activated.", "user": serialize_user(user)}, 200


class UserHardDeleteResource(Resource):
    method_decorators = [role_required("admin")]

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        if user.role == "admin":
            return {"message": "Admin account cannot be deleted."}, 403

        current = get_current_user()
        if current and current.id == user.id:
            return {"message": "Cannot hard-delete your own account."}, 400

        db.session.delete(user)
        db.session.commit()
        return {"message": "User permanently deleted."}, 200


class CategoryCatalogResource(Resource):
    method_decorators = [role_required("manager", "staff", "admin")]

    def get(self):
        user = get_current_user()
        allowed = list(DEFAULT_TASK_CATEGORIES)
        if user.role == "manager":
            allowed = TaskService.get_manager_categories(user.id)

        return {
            "all_categories": DEFAULT_TASK_CATEGORIES,
            "allowed_categories": allowed,
        }, 200


class ManagerCategoryListResource(Resource):
    method_decorators = [role_required("admin")]

    def get(self):
        managers = User.query.filter_by(role="manager").order_by(User.created_at.desc()).all()
        return {
            "items": [serialize_user(manager) for manager in managers],
            "categories": DEFAULT_TASK_CATEGORIES,
        }, 200


class ManagerCategoryAssignResource(Resource):
    method_decorators = [role_required("admin")]

    def put(self, user_id):
        manager = User.query.get_or_404(user_id)
        if manager.role != "manager":
            return {"message": "Target user must be a manager."}, 400

        payload = request.get_json(silent=True) or {}
        categories = payload.get("categories")
        if not isinstance(categories, list):
            return {"message": "categories must be an array."}, 400

        normalized = []
        for item in categories:
            value = normalize_category(item)
            if value is None:
                return {
                    "message": f"Invalid category '{item}'. Allowed: {', '.join(DEFAULT_TASK_CATEGORIES)}"
                }, 400
            if value not in normalized:
                normalized.append(value)

        TaskService.set_manager_categories(manager, normalized)
        return {
            "message": "Manager categories updated.",
            "manager": serialize_user(manager),
        }, 200


def register_resources(api):
    api.add_resource(MeResource, "/users/me")
    api.add_resource(UserListResource, "/users")
    api.add_resource(CategoryCatalogResource, "/users/categories")
    api.add_resource(ManagerCategoryListResource, "/users/manager-categories")
    api.add_resource(ManagerCategoryAssignResource, "/users/<int:user_id>/categories")
    api.add_resource(UserDetailResource, "/users/<int:user_id>")
    api.add_resource(UserTerminateResource, "/users/<int:user_id>/terminate")
    api.add_resource(UserActivateResource, "/users/<int:user_id>/activate")
    api.add_resource(UserHardDeleteResource, "/users/<int:user_id>/hard")
