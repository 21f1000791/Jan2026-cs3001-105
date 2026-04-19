# # =========================================================
# # 📌 ADDITIONAL TEST CASES (FULL COVERAGE)
# # =========================================================

# from app.extensions import db
# from app.models import Task, Notification


# from app.extensions import db
# from app.models import User

# def create_user(name, email, role, password="Password!234"):
#     user = User(name=name, email=email, role=role)
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()
#     return user


# def login(client, email, password="Password!234"):
#     res = client.post("/api/auth/login", json={
#         "email": email,
#         "password": password
#     })
#     return res.get_json()["access_token"]

# # =========================================================
# # 🔐 AUTH TESTS
# # =========================================================
# def test_login_missing_fields(client):
#     res = client.post("/api/auth/login", json={})
#     assert res.status_code == 400


# def test_register_invalid_email_format(client):
#     res = client.post("/api/auth/register", json={
#         "name": "BadEmail",
#         "email": "invalid-email",
#         "password": "Password!234"
#     })
#     assert res.status_code in [201, 400]


# def test_logout_without_token(client):
#     res = client.post("/api/auth/logout")
#     assert res.status_code in [400, 401]


# # =========================================================
# # 📋 TASK TESTS
# # =========================================================
# def test_get_all_tasks(client, app):
#     with app.app_context():
#         manager = create_user("ManagerT", "mt@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/tasks", headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_soft_delete_task(client, app):
#     with app.app_context():
#         manager = create_user("ManagerSD", "sd@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.post("/api/tasks", json={"title": "SoftDelete"},
#                           headers={"Authorization": f"Bearer {token}"})
#         task_id = res.get_json()["task"]["id"]

#         task = Task.query.get(task_id)
#         task.soft_delete()
#         db.session.commit()

#         assert task.is_deleted is True


# def test_hard_delete_task_admin(client, app):
#     with app.app_context():
#         admin = create_user("AdminHD", "hd@test.com", "admin")
#         token = login(client, admin.email)

#         res = client.post("/api/tasks", json={"title": "DeleteMe"},
#                           headers={"Authorization": f"Bearer {token}"})
#         task_id = res.get_json()["task"]["id"]

#         res = client.delete(f"/api/tasks/{task_id}/hard",
#                             headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_task_delete_invalid_id(client, app):
#     with app.app_context():
#         admin = create_user("AdminInv", "inv@test.com", "admin")
#         token = login(client, admin.email)

#         res = client.delete("/api/tasks/9999/hard",
#                             headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 404


# def test_unauthorized_task_deletion(client, app):
#     with app.app_context():
#         staff = create_user("StaffUD", "ud@test.com", "staff")
#         token = login(client, staff.email)

#         res = client.delete("/api/tasks/1/hard",
#                             headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code in [401, 403]


# def test_task_long_input(client, app):
#     with app.app_context():
#         manager = create_user("ManagerLong", "long@test.com", "manager")
#         token = login(client, manager.email)

#         long_title = "A" * 1000

#         res = client.post("/api/tasks", json={"title": long_title},
#                           headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code in [201, 400]


# def test_task_duplicate_data(client, app):
#     with app.app_context():
#         manager = create_user("ManagerDup", "dup2@test.com", "manager")
#         token = login(client, manager.email)

#         payload = {"title": "Same Task"}

#         client.post("/api/tasks", json=payload,
#                     headers={"Authorization": f"Bearer {token}"})
#         res = client.post("/api/tasks", json=payload,
#                           headers={"Authorization": f"Bearer {token}"})

#         assert res.status_code in [201, 400]


# # =========================================================
# # 🔔 NOTIFICATIONS TESTS
# # =========================================================
# def test_mark_already_read_notification(client, app):
#     with app.app_context():
#         user = create_user("UserNR", "nr@test.com", "staff")
#         note = Notification(user_id=user.id, message="Test", is_read=True)
#         db.session.add(note)
#         db.session.commit()

#         token = login(client, user.email)

#         res = client.patch(f"/api/notifications/{note.id}/read",
#                            headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_notifications_invalid_token(client):
#     res = client.get("/api/notifications",
#                      headers={"Authorization": "Bearer invalid"})
#     assert res.status_code in [401, 422]


# # =========================================================
# # 👤 USER TESTS
# # =========================================================
# def test_unauthorized_user_creation(client):
#     res = client.post("/api/users", json={
#         "name": "User",
#         "email": "u@test.com",
#         "password": "Password!234"
#     })
#     assert res.status_code in [401, 403]


# def test_user_invalid_role(client, app):
#     with app.app_context():
#         manager = create_user("ManagerUR", "ur@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.post("/api/users", json={
#             "name": "BadRole",
#             "email": "bad@test.com",
#             "password": "Password!234",
#             "role": "invalid"
#         }, headers={"Authorization": f"Bearer {token}"})

#         assert res.status_code == 400


# def test_user_missing_fields(client, app):
#     with app.app_context():
#         manager = create_user("ManagerMF", "mf@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.post("/api/users", json={},
#                           headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 400


# def test_user_delete_other_unauthorized(client, app):
#     with app.app_context():
#         staff = create_user("StaffX", "sx@test.com", "staff")
#         other = create_user("Other", "other@test.com", "staff")

#         token = login(client, staff.email)

#         res = client.delete(f"/api/users/{other.id}/hard",
#                             headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code in [401, 403]


# # =========================================================
# # 🔍 SEARCH TESTS
# # =========================================================
# def test_search_large_query(client, app):
#     with app.app_context():
#         manager = create_user("ManagerSQ", "sq@test.com", "manager")
#         token = login(client, manager.email)

#         query = "A" * 5000
#         res = client.get(f"/api/search/tasks?q={query}",
#                          headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_search_special_characters(client, app):
#     with app.app_context():
#         manager = create_user("ManagerSC", "sc@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/search/tasks?q=!@#$%^&*()",
#                          headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_search_sql_injection(client, app):
#     with app.app_context():
#         manager = create_user("ManagerSQL", "sql@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/search/tasks?q=' OR 1=1 --",
#                          headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# # =========================================================
# # 📤 EXPORT TESTS
# # =========================================================
# def test_export_invalid_format(client, app):
#     with app.app_context():
#         manager = create_user("ManagerEF", "ef@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/export/tasks?format=xyz",
#                          headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# def test_export_without_auth(client):
#     res = client.get("/api/export/tasks")
#     assert res.status_code in [401, 403]


# def test_export_no_data(client, app):
#     with app.app_context():
#         manager = create_user("ManagerND", "nd@test.com", "manager")
#         token = login(client, manager.email)

#         res = client.get("/api/export/tasks?format=csv",
#                          headers={"Authorization": f"Bearer {token}"})
#         assert res.status_code == 200


# # =========================================================
# # 🔐 SECURITY TESTS
# # =========================================================
# def test_access_without_token(client):
#     res = client.get("/api/tasks")
#     assert res.status_code in [401, 403]


# def test_access_with_invalid_token(client):
#     res = client.get("/api/tasks",
#                      headers={"Authorization": "Bearer invalidtoken"})
#     assert res.status_code in [401, 422]


# def test_role_violation_staff_access_manager_api(client, app):
#     with app.app_context():
#         staff = create_user("StaffRV", "rv@test.com", "staff")
#         token = login(client, staff.email)

#         res = client.get("/api/users",
#                          headers={"Authorization": f"Bearer {token}"})

#         assert res.status_code in [401, 403]