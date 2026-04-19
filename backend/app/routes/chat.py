# app/routes/chat.py
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from app.middleware.authz import role_required
from app.services.chat_service import ChatService

class ChatbotResource(Resource):
    # CRITICAL: Lock this down to managers and admins only!
    method_decorators = [role_required("manager", "admin")]

    def post(self):
        payload = request.get_json(silent=True) or {}
        message = payload.get("message")

        if not message:
            return {"message": "Message is required."}, 400

        reply = ChatService.chat_with_database(message)
        return {"reply": reply}, 200

def register_resources(api):
    api.add_resource(ChatbotResource, "/chat")