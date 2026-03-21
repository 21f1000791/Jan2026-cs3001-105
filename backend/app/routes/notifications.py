from flask import current_app, request
from flask_restful import Resource

from app.middleware.authz import get_current_user, role_required
from app.models import Notification
from app.utils.pagination import build_pagination_meta, parse_pagination_args
from app.utils.serializers import serialize_notification


class NotificationListResource(Resource):
	method_decorators = [role_required("manager", "staff", "admin")]

	def get(self):
		user = get_current_user()
		page, per_page = parse_pagination_args(
			request.args,
			default_page=current_app.config["DEFAULT_PAGE"],
			default_page_size=current_app.config["DEFAULT_PAGE_SIZE"],
			max_page_size=current_app.config["MAX_PAGE_SIZE"],
		)
		query = Notification.query.filter(Notification.user_id == user.id).order_by(Notification.timestamp.desc())
		pagination = query.paginate(page=page, per_page=per_page, error_out=False)
		return {
			"items": [serialize_notification(n) for n in pagination.items],
			"meta": build_pagination_meta(pagination),
		}, 200


class NotificationUnreadResource(Resource):
	method_decorators = [role_required("manager", "staff", "admin")]

	def get(self):
		user = get_current_user()
		items = (
			Notification.query.filter(Notification.user_id == user.id, Notification.is_read.is_(False))
			.order_by(Notification.timestamp.desc())
			.all()
		)
		return {"items": [serialize_notification(n) for n in items]}, 200


class NotificationReadResource(Resource):
	method_decorators = [role_required("manager", "staff", "admin")]

	def patch(self, notification_id):
		from app.extensions import db

		user = get_current_user()
		notification = Notification.query.get_or_404(notification_id)
		if notification.user_id != user.id:
			return {"message": "Insufficient permissions."}, 403

		notification.is_read = True
		db.session.commit()
		return {"message": "Notification marked as read.", "notification": serialize_notification(notification)}, 200


def register_resources(api):
	api.add_resource(NotificationListResource, "/notifications")
	api.add_resource(NotificationUnreadResource, "/notifications/unread")
	api.add_resource(NotificationReadResource, "/notifications/<int:notification_id>/read")
