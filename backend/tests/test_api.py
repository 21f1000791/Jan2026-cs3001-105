from app.extensions import db
from app.models import Notification, Task, TaskStatusHistory, User


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


def test_auth_register_login_logout(client, app):
    register_resp = client.post(
        "/api/auth/register",
        json={
            "name": "Manager User",
            "email": "manager@cop.local",
            "password": "Password!234",
            "role": "manager",
        },
    )
    assert register_resp.status_code == 201

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "manager@cop.local", "password": "Password!234"},
    )
    assert login_resp.status_code == 200
    token = login_resp.get_json()["access_token"]

    logout_resp = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_resp.status_code == 200

    # Token should be revoked for subsequent protected access.
    me_resp = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 401


def test_task_creation_by_manager(client, app):
    with app.app_context():
        manager = _create_user("Manager", "task.manager@cop.local", "manager")
        staff = _create_user("Staff", "task.staff@cop.local", "staff")

        token = _login(client, manager.email)

        payload = {
            "title": "Prepare weekly ledger",
            "description": "Compile all invoices and ledger entries.",
            "category": "finance",
            "priority": "high",
            "status": "todo",
            "assigned_to": staff.id,
            "multilingual_enabled": True,
        }
        response = client.post("/api/tasks", json=payload, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201

        task = Task.query.filter_by(title="Prepare weekly ledger").first()
        assert task is not None
        assert task.assigned_to == staff.id

        history = TaskStatusHistory.query.filter_by(task_id=task.id).all()
        assert len(history) >= 1

        assignment_notification = Notification.query.filter_by(user_id=staff.id).first()
        assert assignment_notification is not None


def test_staff_status_update_records_history(client, app):
    with app.app_context():
        manager = _create_user("Manager2", "manager2@cop.local", "manager")
        staff = _create_user("Staff2", "staff2@cop.local", "staff")

        task = Task(
            title="Close support tickets",
            description="Resolve assigned tickets",
            category="support",
            priority="medium",
            status="todo",
            assigned_to=staff.id,
            created_by=manager.id,
        )
        db.session.add(task)
        db.session.commit()

        token = _login(client, staff.email)
        response = client.patch(
            f"/api/tasks/{task.id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        db.session.refresh(task)
        assert task.status == "in_progress"

        history = TaskStatusHistory.query.filter_by(task_id=task.id, status="in_progress").all()
        assert len(history) == 1


def test_notifications_list_and_read(client, app):
    with app.app_context():
        staff = _create_user("Staff3", "staff3@cop.local", "staff")
        note = Notification(user_id=staff.id, message="Test notification")
        db.session.add(note)
        db.session.commit()

        token = _login(client, staff.email)

        list_resp = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
        assert list_resp.status_code == 200
        items = list_resp.get_json()["items"]
        assert len(items) == 1
        assert items[0]["is_read"] is False

        read_resp = client.patch(
            f"/api/notifications/{note.id}/read",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert read_resp.status_code == 200

        db.session.refresh(note)
        assert note.is_read is True
