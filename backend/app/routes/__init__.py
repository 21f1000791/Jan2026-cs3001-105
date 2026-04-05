import os

from flask import Blueprint, jsonify
from flask import Response
from flask_restful import Api

from . import auth, dashboard, export, notifications, search, tasks, translations, users

api_bp = Blueprint("api", __name__)
api = Api(api_bp)
_api_resources_registered = False


@api_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "community-ops-backend"}), 200


@api_bp.get("/docs/openapi.yaml")
def openapi_spec():
    spec_path = os.path.abspath(os.path.join(api_bp.root_path, "..", "..", "openapi.yaml"))
    if not os.path.exists(spec_path):
        return jsonify({"message": "OpenAPI spec not found."}), 404

    with open(spec_path, "r", encoding="utf-8") as handle:
        content = handle.read()
    return Response(content, mimetype="application/yaml")


@api_bp.get("/docs")
def swagger_ui():
    html = """
<!doctype html>
<html>
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Community Ops API Docs</title>
        <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui.css\" />
    </head>
    <body>
        <div id=\"swagger-ui\"></div>
        <script src=\"https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js\"></script>
        <script>
            window.ui = SwaggerUIBundle({
                url: '/api/docs/openapi.yaml',
                dom_id: '#swagger-ui',
                presets: [SwaggerUIBundle.presets.apis],
                layout: 'BaseLayout',
            });
        </script>
    </body>
</html>
"""
    return Response(html, mimetype="text/html")


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
    translations.register_resources(api)
    _api_resources_registered = True
