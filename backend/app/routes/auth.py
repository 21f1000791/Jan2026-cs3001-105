from flask import request
from flask_jwt_extended import get_jwt, jwt_required
from flask_restful import Resource

from app.services.auth_service import AuthService
from app.utils.serializers import serialize_user


class RegisterResource(Resource):
	def post(self):
		payload = request.get_json(silent=True) or {}
		name = (payload.get("name") or "").strip()
		email = (payload.get("email") or "").strip()
		password = payload.get("password") or ""
		role = payload.get("role", "staff")

		if not name or not email or not password:
			return {"message": "name, email, and password are required."}, 400
		if role not in {"manager", "staff", "admin"}:
			return {"message": "Invalid role."}, 400

		user, error = AuthService.register_user(name=name, email=email, password=password, role=role)
		if error:
			return {"message": error}, 409

		logged_in_user, token, _ = AuthService.login_user(email=email, password=password)
		return {
			"message": "Registration successful.",
			"access_token": token,
			"user": serialize_user(logged_in_user),
		}, 201


class LoginResource(Resource):
	def post(self):
		payload = request.get_json(silent=True) or {}
		email = (payload.get("email") or "").strip()
		password = payload.get("password") or ""

		if not email or not password:
			return {"message": "email and password are required."}, 400

		user, token, error = AuthService.login_user(email=email, password=password)
		if error:
			return {"message": error}, 401

		return {
			"message": "Login successful.",
			"access_token": token,
			"token": token,
			"role": user.role,
			"user": serialize_user(user),
		}, 200


class LogoutResource(Resource):
	@jwt_required()
	def post(self):
		encoded = request.headers.get("Authorization", "").replace("Bearer ", "", 1).strip()
		if not encoded:
			return {"message": "Missing bearer token."}, 400

		claims = get_jwt()
		if not claims.get("jti"):
			return {"message": "Invalid token claims."}, 400

		AuthService.revoke_token(encoded)
		return {"message": "Logout successful."}, 200


def register_resources(api):
	api.add_resource(RegisterResource, "/auth/register")
	api.add_resource(LoginResource, "/auth/login")
	api.add_resource(LogoutResource, "/auth/logout")
