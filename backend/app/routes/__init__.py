from flask import Blueprint, jsonify
from flask_restful import Api

from . import auth, dashboard, export, notifications, search, tasks, users

api_bp = Blueprint("api", __name__)
api = Api(api_bp)
_api_resources_registered = False


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "community-ops-backend"}), 200


def register_api_resources():
    global _api_resources_registered
    if _api_resources_registered:
        return

    auth.register_resources(api)
    tasks.register_resources(api)
    notifications.register_resources(api)
    search.register_resources(api)
    dashboard.register_resources(api)
    export.register_resources(api)
    users.register_resources(api)
    _api_resources_registered = True
