import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.extensions import db, jwt, migrate
from app.models.token_blocklist import TokenBlocklist


@jwt.token_in_blocklist_loader
def is_token_revoked(_jwt_header, jwt_payload):
    jti = jwt_payload.get("jti")
    if not jti:
        return True
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None


def create_app(config_name=None):
    load_dotenv()
    from app.config import CONFIG_MAP

    app = Flask(__name__)

    selected_config = config_name or os.getenv("FLASK_CONFIG", "development")
    app.config.from_object(CONFIG_MAP[selected_config])

    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models to ensure SQLAlchemy metadata is populated for migrations.
    from app import models  # noqa: F401
    from app.routes import api_bp, register_api_resources

    register_api_resources()

    app.register_blueprint(api_bp, url_prefix=app.config["API_PREFIX"])
    return app
