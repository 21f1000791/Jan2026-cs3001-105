from app.config.development import DevelopmentConfig
from app.config.production import ProductionConfig
from app.config.testing import TestingConfig


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
