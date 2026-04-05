from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.middleware.authz import get_current_user, role_required
from app.models import Task
from app.services.task_service import TaskService
from app.services.translation_service import TranslationService
from app.utils.pagination import build_pagination_meta, parse_pagination_args
from app.utils.serializers import serialize_task


class ManagerTaskListResource(Resource):
	method_decorators = [role_required("manager", "admin")]

	def get(self):
		user = get_current_user()
		page, per_page = parse_pagination_args(
			request.args,
			default_page=current_app.config["DEFAULT_PAGE"],
			default_page_size=current_app.config["DEFAULT_PAGE_SIZE"],
			max_page_size=current_app.config["MAX_PAGE_SIZE"],
		)
		filters = {
			"status": request.args.get("status"),
			"category": request.args.get("category"),
			"date": request.args.get("date"),
			"q": request.args.get("q"),
			"actor": user,
		}

		include_deleted = request.args.get("include_deleted", "false").lower() == "true"
		query = TaskService.list_tasks(filters, include_deleted=include_deleted)
		pagination = query.paginate(page=page, per_page=per_page, error_out=False)

		return {
			"items": [serialize_task(t) for t in pagination.items],
			"meta": build_pagination_meta(pagination),
		}, 200

	def post(self):
		payload = request.get_json(silent=True) or {}
		user = get_current_user()
		task, error = TaskService.create_task(payload, creator_id=user.id, actor=user)
		if error:
			status = 403 if "permission" in error.lower() else 400
			return {"message": error}, status
		return {"message": "Task created.", "task": serialize_task(task)}, 201


class TaskDetailResource(Resource):
	@jwt_required()
	def get(self, task_id):
		task = Task.query.get_or_404(task_id)
		user = get_current_user()

		if task.is_deleted and user.role != "admin":
			return {"message": "Task not found."}, 404

		if not TaskService.can_access_task(user, task):
			return {"message": "Insufficient permissions."}, 403

		return {"task": serialize_task(task)}, 200


class ManagerTaskMutationResource(Resource):
	method_decorators = [role_required("manager", "admin")]

	def put(self, task_id):
		task = Task.query.get_or_404(task_id)
		user = get_current_user()
		if not TaskService.can_access_task(user, task):
			return {"message": "Insufficient permissions."}, 403

		payload = request.get_json(silent=True) or {}
		task, error = TaskService.update_task(task, payload, actor=user)
		if error:
			status = 403 if "permission" in error.lower() else 400
			return {"message": error}, status
		return {"message": "Task updated.", "task": serialize_task(task)}, 200

	def delete(self, task_id):
		from app.extensions import db

		task = Task.query.get_or_404(task_id)
		user = get_current_user()
		if not TaskService.can_access_task(user, task):
			return {"message": "Insufficient permissions."}, 403

		db.session.delete(task)
		db.session.commit()
		return {"message": "Task permanently deleted."}, 200


class TaskHardDeleteResource(Resource):
	method_decorators = [role_required("admin")]

	def delete(self, task_id):
		from app.extensions import db

		task = Task.query.get_or_404(task_id)
		db.session.delete(task)
		db.session.commit()
		return {"message": "Task permanently deleted."}, 200


class StaffAssignedTasksResource(Resource):
	method_decorators = [role_required("staff")]

	def get(self):
		user = get_current_user()
		language = (request.args.get("lang") or "en").strip().lower()
		page, per_page = parse_pagination_args(
			request.args,
			default_page=current_app.config["DEFAULT_PAGE"],
			default_page_size=current_app.config["DEFAULT_PAGE_SIZE"],
			max_page_size=current_app.config["MAX_PAGE_SIZE"],
		)
		query = Task.query.filter(Task.assigned_to == user.id, Task.is_deleted.is_(False)).order_by(Task.created_at.desc())
		pagination = query.paginate(page=page, per_page=per_page, error_out=False)

		items = [serialize_task(t) for t in pagination.items]
		if language != "en":
			texts = []
			for item in items:
				if item.get("title"):
					texts.append(item["title"])
				if item.get("category"):
					texts.append(item["category"])
				if item.get("description"):
					texts.append(item["description"])

			translated_map = TranslationService.translate_texts(texts, language)
			for item in items:
				item["translated_title"] = translated_map.get(item.get("title") or "", item.get("title") or "")
				item["translated_category"] = translated_map.get(item.get("category") or "", item.get("category") or "")

				description_text = item.get("description") or ""
				existing = ""
				for tr in item.get("translations", []):
					if tr.get("language") == language and tr.get("translated_text"):
						existing = tr.get("translated_text")
						break

				item["description"] = existing or translated_map.get(description_text, description_text)

		return {
			"items": items,
			"meta": build_pagination_meta(pagination),
		}, 200


class StaffTaskStatusResource(Resource):
	method_decorators = [jwt_required()]

	def patch(self, task_id):
		payload = request.get_json(silent=True) or {}
		status = payload.get("status")
		if status not in {"todo", "in_progress", "blocked", "completed", "overdue"}:
			return {"message": "Invalid status."}, 400

		task = Task.query.get_or_404(task_id)
		user = get_current_user()
		if not TaskService.can_access_task(user, task):
			return {"message": "Insufficient permissions."}, 403

		task, error = TaskService.set_task_status(task, status, actor=user)
		if error:
			return {"message": error}, 403
		return {"message": "Task status updated.", "task": serialize_task(task)}, 200


def register_resources(api):
	api.add_resource(ManagerTaskListResource, "/tasks", endpoint="manager_tasks")
	api.add_resource(ManagerTaskListResource, "/tasks/all", endpoint="manager_tasks_all")
	api.add_resource(TaskDetailResource, "/tasks/<int:task_id>")
	api.add_resource(ManagerTaskMutationResource, "/tasks/<int:task_id>")
	api.add_resource(TaskHardDeleteResource, "/tasks/<int:task_id>/hard")
	api.add_resource(StaffAssignedTasksResource, "/tasks/assigned", endpoint="staff_tasks_assigned")
	api.add_resource(StaffAssignedTasksResource, "/tasks/my-tasks", endpoint="staff_tasks_mine")
	api.add_resource(StaffTaskStatusResource, "/tasks/<int:task_id>/status")
