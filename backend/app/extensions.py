from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Centralized extension singletons for app factory pattern.
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
