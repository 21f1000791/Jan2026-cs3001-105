from flask import request
from flask_restful import Resource

from app.middleware.authz import role_required
from app.services.translation_service import TranslationService


class UITranslationResource(Resource):
    method_decorators = [role_required("manager", "staff", "admin")]

    def post(self):
        payload = request.get_json(silent=True) or {}
        language = (payload.get("language") or "en").strip().lower()
        texts = payload.get("texts") or {}

        if not isinstance(texts, dict):
            return {"message": "texts must be an object map."}, 400

        normalized = {}
        for key, value in texts.items():
            normalized[str(key)] = str(value or "")

        translated = TranslationService.translate_mapping(normalized, language)
        return {
            "language": language,
            "translations": translated,
        }, 200


def register_resources(api):
    api.add_resource(UITranslationResource, "/translations/ui")
