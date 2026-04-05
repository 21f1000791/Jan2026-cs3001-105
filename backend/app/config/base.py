import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this-at-least-32-chars")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-this-at-least-32-chars")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///community_ops.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_TOKEN_LOCATION = ["headers"]
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/1"))
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
    SARVAM_MODEL = os.getenv("SARVAM_MODEL", "sarvam-m")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Pagination defaults for future API modules.
    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
