from app import create_app
from app.config.celery import make_celery
from app.services.jobs import register_periodic_jobs

flask_app = create_app()
celery = make_celery(flask_app)
register_periodic_jobs(celery)
