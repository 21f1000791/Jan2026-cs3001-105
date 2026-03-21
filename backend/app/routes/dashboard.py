from flask_restful import Resource

from app.middleware.authz import get_current_user, role_required
from app.services.dashboard_service import DashboardService


class ManagerDashboardResource(Resource):
	method_decorators = [role_required("manager", "admin")]

	def get(self):
		return {"metrics": DashboardService.manager_metrics()}, 200


class StaffDashboardResource(Resource):
	method_decorators = [role_required("staff", "manager", "admin")]

	def get(self):
		user = get_current_user()
		return {"metrics": DashboardService.staff_metrics(user.id)}, 200


def register_resources(api):
	api.add_resource(ManagerDashboardResource, "/dashboard/manager")
	api.add_resource(StaffDashboardResource, "/dashboard/staff")
