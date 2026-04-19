# """
# FULL BACKEND TEST SUITE
# Covers:
# 1. Auth (Positive, Negative, Edge)
# 2. Tasks (CRUD, validation, edge cases)
# 3. Notifications
# 4. Users
# 5. Search
# 6. Export
# 7. Security / Role-based access
# """

# from app.extensions import db
# from app.models import User, Task, Notification, TaskStatusHistory


# # =========================================================
# # 🔧 HELPERS
# # =========================================================
# def create_user(name, email, role, password="Password!234", is_active=True):
#     user = User(name=name, email=email, role=role, is_active=is_active)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()
#     return user


# def login(client, email, password="Password!234"):
#     res = client.post("/api/auth/login", json={"email": email, "password": password})
#     return res.get_json().get("access_token")


# # =========================================================
# # 🔐 AUTH TESTS
# # =========================================================
# def test_auth_positive_flow(client):
#     res = client.post("/api/auth/register", json={
#         "name": "AuthUser",
#         "email": "auth@test.com",
#         "password": "Password!234",
#         "role": "manager"
#     })
#     assert res.status_code == 201

#     login_res = client.post("/api/auth/login", json={
#         "email": "auth@test.com",
#         "password": "Password!234"
#     })
#     assert login_res.status_code == 200

#     token = login_res.get_json()["access_token"]

#     logout_res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
#     assert logout_res.status_code == 200


# def test_auth_negative_cases(client, app):
#     # Duplicate email
#     client.post("/api/auth/register", json={
#         "name": "User1", "email": "dup@test.com", "password": "Password!234"
#     })
#     res = client.post("/api/auth/register", json={
#         "name": "User2", "email": "dup@test.com", "password": "Password!234"
#     })
#     assert res.status_code == 409

#     # Wrong password
#     res = client.post("/api/auth/login", json={
#         "email": "dup@test.com", "password": "wrong"
#     })
#     assert res.status_code == 401

#     # Inactive user
#     with app.app_context():
#         user = create_user("Inactive", "inactive@test.com", "staff", is_active=False)

#     res = client.post("/api/auth/login", json={
#         "email": "inactive@test.com", "password": "Password!234"
#     })
#     assert res.status_code == 401


# # =========================================================
# # 📋 TASK TESTS
# # =========================================================
# def test_task_creation_and_assignment(client, app):
#     with app.app_context():
#         manager = create_user("Manager", "m@test.com", "manager")
#         staff = create_user("Staff", "s@test.com", "staff")

#         token = login(client, manager.email)

#         res = client.post("/api/tasks", json={
#             "title": "Task1",
#             "priority": "high",
#             "assigned_to": staff.id
#         }, headers={"Authorization": f"Bearer {token}"})

#         assert res.status_code == 201

#         task = Task.query.first()
#         assert task.assigned_to == staff.id

#         # Notification created
#         notif = Notification.query.filter_by(user_id=staff.id).first()
#         assert notif is not None


# def test_task_negative_cases(client, app):
#     with app.app_context():
#         manager = create_user("Manager2", "m2@test.com", "manager")
#         token = login(client, manager.email)

#         # Missing title
#         res = client.post("/api/tasks", json={}, headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 400

#         # Invalid priority
#         res = client.post("/api/tasks", json={
#             "title": "BadTask", "priority": "invalid"
#         }, headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 400

#         # Invalid assigned user
#         res = client.post("/api/tasks", json={
#             "title": "Task", "assigned_to": 999
#         }, headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 400


# def test_task_status_update_and_history(client, app):
#     with app.app_context():
#         manager = create_user("Manager3", "m3@test.com", "manager")
#         staff = create_user("Staff3", "s3@test.com", "staff")

#         task = Task(title="Test", status="todo", created_by=manager.id, assigned_to=staff.id)
#         db.session.add(task)
#         db.session.commit()

#         token = login(client, staff.email)

#         res = client.patch(
#             f"/api/tasks/{task.id}/status",
#             json={"status": "in_progress"},
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         assert res.status_code == 200

#         history = TaskStatusHistory.query.filter_by(task_id=task.id).all()
#         assert len(history) >= 1


# def test_task_security(client, app):
#     with app.app_context():
#         manager = create_user("Manager4", "m4@test.com", "manager")
#         staff1 = create_user("Staff1", "s1@test.com", "staff")
#         staff2 = create_user("Staff2", "s2@test.com", "staff")

#         task = Task(title="Private", status="todo", created_by=manager.id, assigned_to=staff1.id)
#         db.session.add(task)
#         db.session.commit()

#         token = login(client, staff2.email)

#         res = client.patch(
#             f"/api/tasks/{task.id}/status",
#             json={"status": "completed"},
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         assert res.status_code == 403


# # =========================================================
# # 🔔 NOTIFICATION TESTS
# # =========================================================
# def test_notifications_flow(client, app):
#     with app.app_context():
#         user = create_user("UserN", "n@test.com", "staff")

#         note = Notification(user_id=user.id, message="Hello")
#         db.session.add(note)
#         db.session.commit()

#         token = login(client, user.email)

#         res = client.get("/api/notifications", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200

#         res = client.patch(
#             f"/api/notifications/{note.id}/read",
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         assert res.status_code == 200


# def test_notification_security(client, app):
#     with app.app_context():
#         user1 = create_user("U1", "u1@test.com", "staff")
#         user2 = create_user("U2", "u2@test.com", "staff")

#         note = Notification(user_id=user1.id, message="Private")
#         db.session.add(note)
#         db.session.commit()

#         token = login(client, user2.email)

#         res = client.patch(
#             f"/api/notifications/{note.id}/read",
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         assert res.status_code == 403


# # =========================================================
# # 👤 USER TESTS
# # =========================================================
# def test_user_management(client, app):
#     with app.app_context():
#         manager = create_user("ManagerU", "mu@test.com", "manager")
#         token = login(client, manager.email)

#         # Create user
#         res = client.post("/api/users", json={
#             "name": "NewUser",
#             "email": "new@test.com",
#             "password": "Password!234",
#             "role": "staff"
#         }, headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 201

#         # Duplicate email
#         res = client.post("/api/users", json={
#             "name": "NewUser",
#             "email": "new@test.com",
#             "password": "Password!234",
#             "role": "staff"
#         }, headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 409


# def test_user_delete_self(client, app):
#     with app.app_context():
#         admin = create_user("Admin", "admin@test.com", "admin")
#         token = login(client, admin.email)

#         res = client.delete(
#             f"/api/users/{admin.id}/hard",
#             headers={"Authorization": f"Bearer {token}"}
#         )
#         assert res.status_code == 400


# # =========================================================
# # 🔍 SEARCH TESTS
# # =========================================================
# def test_search_tasks(client, app):
#     with app.app_context():
#         manager = create_user("ManagerS", "ms@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/search/tasks?q=test", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200

#         # Edge: empty query
#         res = client.get("/api/search/tasks", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# # =========================================================
# # 📤 EXPORT TESTS
# # =========================================================
# def test_export_endpoints(client, app):
#     with app.app_context():
#         manager = create_user("ManagerE", "me@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/export/tasks?format=csv", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200
#         assert res.mimetype == "text/csv"

#         res = client.get("/api/export/tasks?format=pdf", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200
#         assert res.mimetype == "application/pdf"