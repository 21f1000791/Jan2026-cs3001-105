from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import User


def role_required(*roles):
    allowed_roles = set(roles)

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            try:
                user_id = int(user_id)
            except (TypeError, ValueError):
                return jsonify({"message": "Invalid token identity."}), 401
            user = db.session.get(User, user_id)

            if user is None:
                return jsonify({"message": "User not found."}), 404
            if user.role not in allowed_roles:
                return jsonify({"message": "Insufficient permissions."}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user():
    user_id = get_jwt_identity()
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, user_id)
