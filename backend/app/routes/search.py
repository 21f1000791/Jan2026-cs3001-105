from flask import current_app, request
from flask_restful import Resource

from app.middleware.authz import role_required
from app.services.search_service import SearchService
from app.utils.pagination import build_pagination_meta, parse_pagination_args
from app.utils.serializers import serialize_task


class TaskSearchResource(Resource):
	method_decorators = [role_required("manager", "staff", "admin")]

	def get(self):
		query_text = (request.args.get("q") or "").strip()
		page, per_page = parse_pagination_args(
			request.args,
			default_page=current_app.config["DEFAULT_PAGE"],
			default_page_size=current_app.config["DEFAULT_PAGE_SIZE"],
			max_page_size=current_app.config["MAX_PAGE_SIZE"],
		)
		query = SearchService.search_tasks(query_text=query_text, include_deleted=False)
		pagination = query.paginate(page=page, per_page=per_page, error_out=False)
		return {
			"items": [serialize_task(task) for task in pagination.items],
			"meta": build_pagination_meta(pagination),
			"query": query_text,
		}, 200


def register_resources(api):
	api.add_resource(TaskSearchResource, "/search/tasks")
