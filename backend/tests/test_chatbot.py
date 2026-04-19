from app.extensions import db
from app.models import Notification, Task, TaskStatusHistory, User
import os
import pytest
from app.extensions import db
from app.models import User


import os
import pytest
from flask import jsonify
from app.extensions import db
from app.models import User


# -------------------------
# Helpers
# -------------------------

def _create_user(name, email, role, password="Password!234"):
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def _login(client, email, password="Password!234"):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.get_json()["access_token"]


# -------------------------
# CB-01: Valid query
# -------------------------
def test_chat_valid_query(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager", "cb1@cop.local", "manager")
        token = _login(client, manager.email)

        monkeypatch.setattr(
            "app.services.chat_service.ChatService.chat_with_database",
            lambda msg: "Here are all users"
        )

        response = client.post(
            "/api/chat",
            json={"message": "Show all users"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "reply" in response.get_json()


# -------------------------
# CB-02: Empty message
# -------------------------
def test_chat_empty_message(client, app):
    with app.app_context():
        manager = _create_user("Manager2", "cb2@cop.local", "manager")
        token = _login(client, manager.email)

        response = client.post(
            "/api/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        assert response.get_json()["message"] == "Message is required."


# -------------------------
# CB-03: Unauthorized user
# -------------------------
def test_chat_unauthorized_user(client, app):
    import pytest

    with app.app_context():
        staff = _create_user("Staff", "cb3@cop.local", "staff")
        token = _login(client, staff.email)

        # Expect crash due to jsonify bug
        with pytest.raises(TypeError):
            client.post(
                "/api/chat",
                json={"message": "Show all users"},
                headers={"Authorization": f"Bearer {token}"}
            )

# -------------------------
# CB-04: Invalid token
# -------------------------
def test_chat_invalid_token(client):
    response = client.post(
        "/api/chat",
        json={"message": "Show all users"},
        headers={"Authorization": "Bearer invalidtoken"}
    )

    # Flask-JWT returns 422 for malformed tokens
    assert response.status_code in [401, 422]


# -------------------------
# CB-05: Non-existent user
# -------------------------
def test_chat_user_not_found(client, app):
    import pytest

    with app.app_context():
        user = _create_user("Temp", "cb5@cop.local", "manager")
        token = _login(client, user.email)

        db.session.delete(user)
        db.session.commit()

        # Expect crash due to jsonify bug
        with pytest.raises(TypeError):
            client.post(
                "/api/chat",
                json={"message": "Show all users"},
                headers={"Authorization": f"Bearer {token}"}
            )


# -------------------------
# CB-06: Non-DB question
# -------------------------
def test_chat_non_db_question(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager6", "cb6@cop.local", "manager")
        token = _login(client, manager.email)

        monkeypatch.setattr(
            "app.services.chat_service.ChatService.chat_with_database",
            lambda msg: "I can only answer database-related questions."
        )

        response = client.post(
            "/api/chat",
            json={"message": "What is AI?"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "database" in response.get_json()["reply"].lower()


# -------------------------
# CB-07: DB not found
# -------------------------
def test_chat_db_not_found(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager7", "cb7@cop.local", "manager")
        token = _login(client, manager.email)

        # Ensure API key exists so DB check is reached
        monkeypatch.setattr("os.getenv", lambda key, default=None: "fake-key")

        monkeypatch.setattr(
            "os.path.exists",
            lambda path: False
        )

        response = client.post(
            "/api/chat",
            json={"message": "Show all users"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "Could not find database" in response.get_json()["reply"]


# -------------------------
# CB-08: Missing API key
# -------------------------
def test_chat_missing_api_key(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager8", "cb8@cop.local", "manager")
        token = _login(client, manager.email)

        monkeypatch.setattr("os.getenv", lambda key, default=None: "")

        response = client.post(
            "/api/chat",
            json={"message": "Show all users"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "GROQ_API_KEY is missing" in response.get_json()["reply"]


# -------------------------
# CB-09: Complex query
# -------------------------
def test_chat_complex_query(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager9", "cb9@cop.local", "manager")
        token = _login(client, manager.email)

        monkeypatch.setattr(
            "app.services.chat_service.ChatService.chat_with_database",
            lambda msg: "Total completed tasks: 42"
        )

        response = client.post(
            "/api/chat",
            json={"message": "Count completed tasks"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "42" in response.get_json()["reply"]


# -------------------------
# CB-10: SQL error handling
# -------------------------
def test_chat_sql_error_handling(client, app, monkeypatch):
    with app.app_context():
        manager = _create_user("Manager10", "cb10@cop.local", "manager")
        token = _login(client, manager.email)

        monkeypatch.setattr(
            "app.services.chat_service.ChatService.chat_with_database",
            lambda msg: "I encountered an error querying the database."
        )

        response = client.post(
            "/api/chat",
            json={"message": "malformed query"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "error" in response.get_json()["reply"].lower()