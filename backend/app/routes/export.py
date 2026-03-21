from flask import Response, request
from flask_restful import Resource

from app.middleware.authz import role_required
from app.models import Task
from app.services.export_service import ExportService


class ExportTasksResource(Resource):
	method_decorators = [role_required("manager", "admin")]

	def get(self):
		export_format = (request.args.get("format") or "csv").lower()
		tasks = Task.query.filter(Task.is_deleted.is_(False)).order_by(Task.created_at.desc()).all()

		if export_format == "pdf":
			pdf_bytes = ExportService.export_tasks_pdf(tasks)
			return Response(
				pdf_bytes,
				mimetype="application/pdf",
				headers={"Content-Disposition": "attachment; filename=tasks.pdf"},
			)

		csv_data = ExportService.export_tasks_csv(tasks)
		return Response(
			csv_data,
			mimetype="text/csv",
			headers={"Content-Disposition": "attachment; filename=tasks.csv"},
		)


class ExportPerformanceResource(Resource):
	method_decorators = [role_required("manager", "admin")]

	def get(self):
		csv_data = ExportService.export_performance_csv()
		return Response(
			csv_data,
			mimetype="text/csv",
			headers={"Content-Disposition": "attachment; filename=performance.csv"},
		)


def register_resources(api):
	api.add_resource(ExportTasksResource, "/export/tasks")
	api.add_resource(ExportPerformanceResource, "/export/performance")
