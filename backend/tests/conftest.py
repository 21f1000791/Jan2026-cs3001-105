import pytest

from app import create_app
from app.extensions import db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def db_session(app):
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.remove()
        db.drop_all()
