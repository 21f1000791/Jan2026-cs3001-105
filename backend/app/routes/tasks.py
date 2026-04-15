from flask import current_app, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from app.extensions import db
from app.middleware.authz import get_current_user, role_required
from app.models import Task, Translation
from app.services.task_service import TaskService
from app.services.translation_service import TranslationService
from app.utils.pagination import build_pagination_meta, parse_pagination_args
from app.utils.serializers import serialize_task


def _looks_like_placeholder_translation(text_value, language):
	value = (text_value or "").strip().lower()
	return bool(value) and value.startswith(f"[{language}]")


def _looks_like_reasoning_leak(text_value):
	value = (text_value or "").strip().lower()
	if not value:
		return False
	leak_markers = [
		"<think>",
		"let's tackle",
		"first, i need to",
		"user wants",
		"translation task",
		"double-check",
	]
	return any(marker in value for marker in leak_markers)


def _looks_translated_for_language(text_value, language):
	value = (text_value or "").strip()
	if not value:
		return False

	if language == "hi":
		return any("\u0900" <= ch <= "\u097f" for ch in value)
	if language == "kn":
		return any("\u0c80" <= ch <= "\u0cff" for ch in value)

	return True


def _is_effective_translation(source_text, translated_text):
	source = (source_text or "").strip()
	translated = (translated_text or "").strip()
	if not translated:
		return False
	if translated == source:
		return False
	if _looks_like_reasoning_leak(translated):
		return False
	return True


def _is_valid_cached_translation(source_text, candidate_text, language):
	value = (candidate_text or "").strip()
	if not value:
		return False
	if _looks_like_placeholder_translation(value, language):
		return False
	if _looks_like_reasoning_leak(value):
		return False
	if not _is_effective_translation(source_text, value):
		return False
	if not _looks_translated_for_language(value, language):
		return False
	return True


def _cache_task_translation(task_id, language, source_title, source_description, translated_title, translated_description):
	if language == "en":
		return False

	title_source = (source_title or "").strip()
	text_source = (source_description or "").strip()
	title_value = (translated_title or "").strip()
	text_value = (translated_description or "").strip()

	if not _is_effective_translation(title_source, title_value):
		title_value = ""
	if not _is_effective_translation(text_source, text_value):
		text_value = ""

	if not title_value and not text_value:
		return False

	existing = Translation.query.filter_by(task_id=task_id, language=language).first()
	if existing:
		changed = False
		if title_value and existing.translated_title != title_value:
			existing.translated_title = title_value
			changed = True
		if text_value and existing.translated_text != text_value:
			existing.translated_text = text_value
			changed = True
		return changed

	# DB requires non-null translated_title/translated_text for new rows.
	if not title_value:
		title_value = title_source
	if not text_value:
		text_value = text_source or title_source

	db.session.add(
		Translation(
			task_id=task_id,
			language=language,
			translated_title=title_value,
			translated_text=text_value,
		)
	)
	return True


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
		language = (request.args.get("lang") or "en").strip().lower()

		if task.is_deleted and user.role != "admin":
			return {"message": "Task not found."}, 404

		if not TaskService.can_access_task(user, task):
			return {"message": "Insufficient permissions."}, 403

		item = serialize_task(task)
		cache_updated = False
		if language != "en":
			existing_title = ""
			existing_description = ""
			for tr in item.get("translations", []):
				if tr.get("language") == language:
					if tr.get("translated_title"):
						existing_title = tr.get("translated_title")
					if tr.get("translated_text"):
						existing_description = tr.get("translated_text")
					break

			source_title = (item.get("title") or "").strip()
			source_description = (item.get("description") or "").strip()
			need_title_translation = not _is_valid_cached_translation(source_title, existing_title, language)
			need_description_translation = not _is_valid_cached_translation(source_description, existing_description, language)

			texts_to_translate = []
			if need_title_translation and source_title:
				texts_to_translate.append(source_title)
			if need_description_translation and source_description:
				texts_to_translate.append(source_description)

			translated_map = TranslationService.translate_texts(texts_to_translate, language) if texts_to_translate else {}

			if need_title_translation:
				candidate_title = translated_map.get(source_title, source_title)
				final_title = candidate_title if _is_valid_cached_translation(source_title, candidate_title, language) else source_title
			else:
				final_title = existing_title

			item["translated_title"] = final_title
			item["translated_category"] = TranslationService.localize_category(
				item.get("category") or "", language
			)

			if need_description_translation:
				candidate_description = translated_map.get(source_description, source_description)
				final_description = candidate_description if _is_valid_cached_translation(source_description, candidate_description, language) else source_description
			else:
				final_description = existing_description

			item["translated_description"] = final_description
			item["description"] = item["translated_description"]

			cache_updated = _cache_task_translation(
				task.id,
				language,
				item.get("title") or "",
				item.get("description") or "",
				item.get("translated_title") or "",
				item.get("translated_description") or "",
			)

		if cache_updated:
			db.session.commit()

		return {"task": item}, 200


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
		cache_updated = False
		translation_api_used = False
		if language != "en":
			items_context = []
			texts_to_translate = set()
			for item in items:
				existing_title = ""
				existing_description = ""
				for tr in item.get("translations", []):
					if tr.get("language") == language:
						if tr.get("translated_title"):
							existing_title = tr.get("translated_title")
						if tr.get("translated_text"):
							existing_description = tr.get("translated_text")
						break

				source_title = (item.get("title") or "").strip()
				description_text = item.get("description") or ""
				source_description = description_text.strip()

				need_title_translation = not _is_valid_cached_translation(source_title, existing_title, language)
				need_description_translation = not _is_valid_cached_translation(source_description, existing_description, language)

				if need_title_translation and source_title:
					texts_to_translate.add(source_title)
				if need_description_translation and source_description:
					texts_to_translate.add(source_description)

				items_context.append(
					{
						"item": item,
						"source_title": source_title,
						"source_description": source_description,
						"existing_title": existing_title,
						"existing_description": existing_description,
						"need_title_translation": need_title_translation,
						"need_description_translation": need_description_translation,
					}
				)

			if texts_to_translate:
				translation_api_used = True
			translated_map = TranslationService.translate_texts(list(texts_to_translate), language) if texts_to_translate else {}

			for ctx in items_context:
				item = ctx["item"]
				source_title = ctx["source_title"]
				source_description = ctx["source_description"]

				if ctx["need_title_translation"]:
					candidate_title = translated_map.get(source_title, source_title)
					final_title = candidate_title if _is_valid_cached_translation(source_title, candidate_title, language) else source_title
				else:
					final_title = ctx["existing_title"]

				if ctx["need_description_translation"]:
					candidate_description = translated_map.get(source_description, source_description)
					final_description = candidate_description if _is_valid_cached_translation(source_description, candidate_description, language) else source_description
				else:
					final_description = ctx["existing_description"]

				item["translated_title"] = final_title
				item["translated_category"] = TranslationService.localize_category(
					item.get("category") or "", language
				)
				item["translated_description"] = final_description
				item["description"] = item["translated_description"]

				task_changed = _cache_task_translation(
					item.get("id"),
					language,
					source_title,
					source_description,
					item.get("translated_title") or "",
					item.get("translated_description") or "",
				)
				cache_updated = cache_updated or task_changed

		if cache_updated:
			db.session.commit()

		meta = build_pagination_meta(pagination)
		meta["translation_api_used"] = translation_api_used
		return {
			"items": items,
			"meta": meta,
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
