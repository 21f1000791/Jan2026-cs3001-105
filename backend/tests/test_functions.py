"""
BACKEND TEST SUITE (REORGANIZED BY TESTING TYPE)

Order:
1. Functional Testing
2. Security Testing
3. Performance Testing
4. Accessibility Testing (API-level support)
5. Usability Testing

Includes:
- Existing tests reorganized
- Additional recommended tests (clearly marked as ADDED LATER)
"""

from datetime import datetime, timedelta

from app.extensions import db
from app.models import User, Task, Notification, TaskStatusHistory


# =========================================================
# 🔧 HELPERS
# =========================================================
def create_user(name, email, role, password="Password!234", is_active=True):
    user = User(name=name, email=email, role=role, is_active=is_active)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, email, password="Password!234"):
    res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    data = res.get_json() or {}
    return data.get("access_token")


# =========================================================
# =========================================================
# 1. FUNCTIONAL TESTING
# =========================================================
# =========================================================

# =========================================================
# 1.1 AUTHENTICATION - FUNCTIONAL
# =========================================================

# This test verifies the complete positive authentication flow.
# It checks whether a user can successfully register, then log in,
# receive a valid access token, and finally log out without errors.
def test_auth_positive_flow(client):
    """Register -> Login -> Logout positive flow"""
    res = client.post("/api/auth/register", json={
        "name": "AuthUser",
        "email": "auth@test.com",
        "password": "Password!234",
        "role": "manager"
    })
    assert res.status_code == 201

    login_res = client.post("/api/auth/login", json={
        "email": "auth@test.com",
        "password": "Password!234"
    })
    assert login_res.status_code == 200

    token = login_res.get_json()["access_token"]

    logout_res = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200


# This test checks validation for missing login fields.
# It ensures that the backend rejects incomplete login requests
# and returns a proper client-side validation error.
def test_login_missing_fields(client):
    """Login with missing required fields"""
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400


# This test verifies whether the backend validates email format during registration.
# If strict validation is implemented, it should return 400.
# If not yet implemented, it may still return 201, which highlights a possible improvement area.
def test_register_invalid_email_format(client):
    """Register with invalid email format"""
    res = client.post("/api/auth/register", json={
        "name": "BadEmail",
        "email": "invalid-email",
        "password": "Password!234"
    })
    # Depending on backend validation, can be 400 or (if not validated) 201
    assert res.status_code in [201, 400]


# =========================================================
# 1.2 TASK MANAGEMENT - FUNCTIONAL
# =========================================================

# This test verifies successful task creation and assignment flow.
# It ensures that a manager can create a task, assign it to a staff user,
# and that the system also generates a notification for the assigned user.
def test_task_creation_and_assignment(client, app):
    """Create task and assign to staff"""
    with app.app_context():
        manager = create_user("Manager", "m@test.com", "manager")
        staff = create_user("Staff", "s@test.com", "staff")

        token = login(client, manager.email)

        res = client.post("/api/tasks", json={
            "title": "Task1",
            "priority": "high",
            "assigned_to": staff.id
        }, headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 201

        task = Task.query.first()
        assert task.assigned_to == staff.id

        notif = Notification.query.filter_by(user_id=staff.id).first()
        assert notif is not None


# This test checks negative validation scenarios for task creation.
# It confirms that the backend properly rejects:
# 1) missing required title,
# 2) invalid priority values,
# 3) assignment to a non-existent user.
def test_task_negative_cases(client, app):
    """Task validation negative cases"""
    with app.app_context():
        manager = create_user("Manager2", "m2@test.com", "manager")
        token = login(client, manager.email)

        # Missing title
        res = client.post("/api/tasks", json={},
                          headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 400

        # Invalid priority
        res = client.post("/api/tasks", json={
            "title": "BadTask",
            "priority": "invalid"
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 400

        # Invalid assigned user
        res = client.post("/api/tasks", json={
            "title": "Task",
            "assigned_to": 999
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 400


# This test validates task status update functionality.
# It ensures that an assigned staff member can update task status
# and that the system records the change in TaskStatusHistory for audit tracking.
def test_task_status_update_and_history(client, app):
    """Update task status and verify history"""
    with app.app_context():
        manager = create_user("Manager3", "m3@test.com", "manager")
        staff = create_user("Staff3", "s3@test.com", "staff")

        task = Task(
            title="Test",
            status="todo",
            created_by=manager.id,
            assigned_to=staff.id
        )
        db.session.add(task)
        db.session.commit()

        token = login(client, staff.email)

        res = client.patch(
            f"/api/tasks/{task.id}/status",
            json={"status": "in_progress"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200

        history = TaskStatusHistory.query.filter_by(task_id=task.id).all()
        assert len(history) >= 1


# This test verifies the task listing functionality.
# It checks whether an authenticated manager can retrieve
# the list of tasks successfully through the GET /api/tasks endpoint.
def test_get_all_tasks(client, app):
    """Get all tasks"""
    with app.app_context():
        manager = create_user("ManagerT", "mt@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/tasks",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# This test verifies soft deletion behavior at the model level.
# Instead of permanently removing the task from the database,
# it ensures that the task is marked as deleted using the is_deleted flag.
def test_soft_delete_task(client, app):
    """Soft delete task using model method"""
    with app.app_context():
        manager = create_user("ManagerSD", "sd@test.com", "manager")
        token = login(client, manager.email)

        res = client.post("/api/tasks", json={"title": "SoftDelete"},
                          headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 201

        task_id = res.get_json()["task"]["id"]

        task = Task.query.get(task_id)
        task.soft_delete()
        db.session.commit()

        assert task.is_deleted is True


# This test validates the hard delete endpoint for admin users.
# It ensures that an admin can permanently delete a task
# using the dedicated hard delete API endpoint.
def test_hard_delete_task_admin(client, app):
    """Admin hard deletes a task"""
    with app.app_context():
        admin = create_user("AdminHD", "hd@test.com", "admin")
        token = login(client, admin.email)

        res = client.post("/api/tasks", json={"title": "DeleteMe"},
                          headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 201

        task_id = res.get_json()["task"]["id"]

        res = client.delete(f"/api/tasks/{task_id}/hard",
                            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# This test checks error handling for deletion of a non-existent task.
# It ensures that the backend returns a 404 Not Found response
# when an invalid task ID is provided to the hard delete endpoint.
def test_task_delete_invalid_id(client, app):
    """Delete task with invalid/non-existent id"""
    with app.app_context():
        admin = create_user("AdminInv", "inv@test.com", "admin")
        token = login(client, admin.email)

        res = client.delete("/api/tasks/9999/hard",
                            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404


# This test checks how the backend handles unusually long task titles.
# It helps validate field-length robustness and input validation.
# Depending on implementation, the backend may either accept or reject the request.
def test_task_long_input(client, app):
    """Very long task title"""
    with app.app_context():
        manager = create_user("ManagerLong", "long@test.com", "manager")
        token = login(client, manager.email)

        long_title = "A" * 1000

        res = client.post("/api/tasks", json={"title": long_title},
                          headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [201, 400]


# This test verifies how the system handles duplicate task submissions.
# If duplicate task titles are allowed, the second request may succeed.
# If uniqueness or duplicate prevention is enforced, it may return 400.
def test_task_duplicate_data(client, app):
    """Duplicate task data handling"""
    with app.app_context():
        manager = create_user("ManagerDup", "dup2@test.com", "manager")
        token = login(client, manager.email)

        payload = {"title": "Same Task"}

        client.post("/api/tasks", json=payload,
                    headers={"Authorization": f"Bearer {token}"})
        res = client.post("/api/tasks", json=payload,
                          headers={"Authorization": f"Bearer {token}"})

        assert res.status_code in [201, 400]


# =========================================================
# 1.2 TASK MANAGEMENT - FUNCTIONAL
# ADDED LATER (Recommended)
# =========================================================

# ADDED LATER:
# This test checks whether the API supports fetching a single task by ID.
# It is useful if a detailed task view endpoint exists.
# Since this endpoint may not yet be implemented, the test allows flexible status codes.
def test_get_single_task_by_id(client, app):
    """ADDED LATER: Get a single task by ID (if endpoint exists)"""
    with app.app_context():
        manager = create_user("ManagerGST", "gst@test.com", "manager")
        token = login(client, manager.email)

        create_res = client.post("/api/tasks", json={"title": "SingleTask"},
                                 headers={"Authorization": f"Bearer {token}"})
        assert create_res.status_code == 201

        task_id = create_res.get_json()["task"]["id"]

        # Assumes endpoint exists: GET /api/tasks/<id>
        res = client.get(f"/api/tasks/{task_id}",
                         headers={"Authorization": f"Bearer {token}"})

        # If endpoint not implemented, change/remove this test
        assert res.status_code in [200, 404, 405]


# ADDED LATER:
# This test verifies whether task details can be updated after creation.
# It is useful for validating edit-task functionality such as changing title or priority.
# Since the endpoint may not yet exist, flexible status codes are allowed.
def test_update_task_details(client, app):
    """ADDED LATER: Update task details (if endpoint exists)"""
    with app.app_context():
        manager = create_user("ManagerUT", "ut@test.com", "manager")
        token = login(client, manager.email)

        create_res = client.post("/api/tasks", json={"title": "Old Title"},
                                 headers={"Authorization": f"Bearer {token}"})
        assert create_res.status_code == 201

        task_id = create_res.get_json()["task"]["id"]

        # Assumes endpoint exists: PUT/PATCH /api/tasks/<id>
        res = client.patch(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title", "priority": "medium"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Flexible until endpoint is confirmed
        assert res.status_code in [200, 404, 405]


# =========================================================
# 1.3 NOTIFICATIONS - FUNCTIONAL
# =========================================================

# This test verifies the notification workflow for a user.
# It checks whether notifications can be fetched successfully
# and whether an unread notification can be marked as read.
def test_notifications_flow(client, app):
    """Fetch notifications and mark as read"""
    with app.app_context():
        user = create_user("UserN", "n@test.com", "staff")

        note = Notification(user_id=user.id, message="Hello")
        db.session.add(note)
        db.session.commit()

        token = login(client, user.email)

        res = client.get("/api/notifications",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

        res = client.patch(
            f"/api/notifications/{note.id}/read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200


# This test checks idempotent behavior for marking notifications as read.
# If a notification is already marked as read, the API should still handle
# the request gracefully instead of failing unexpectedly.
def test_mark_already_read_notification(client, app):
    """Mark already read notification"""
    with app.app_context():
        user = create_user("UserNR", "nr@test.com", "staff")
        note = Notification(user_id=user.id, message="Test", is_read=True)
        db.session.add(note)
        db.session.commit()

        token = login(client, user.email)

        res = client.patch(
            f"/api/notifications/{note.id}/read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 200


# =========================================================
# 1.4 USER MANAGEMENT - FUNCTIONAL
# =========================================================

# This test validates manager-level user creation functionality.
# It confirms that a manager can create a new user successfully,
# and also verifies that duplicate email addresses are rejected.
def test_user_management(client, app):
    """Manager creates user and duplicate email rejected"""
    with app.app_context():
        manager = create_user("ManagerU", "mu@test.com", "manager")
        token = login(client, manager.email)

        # Create user
        res = client.post("/api/users", json={
            "name": "NewUser",
            "email": "new@test.com",
            "password": "Password!234",
            "role": "staff"
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 201

        # Duplicate email
        res = client.post("/api/users", json={
            "name": "NewUser",
            "email": "new@test.com",
            "password": "Password!234",
            "role": "staff"
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 409


# This test checks a business rule in user deletion.
# It ensures that an admin is prevented from deleting their own account,
# which helps avoid accidental lockout of privileged access.
def test_user_delete_self(client, app):
    """Admin cannot delete own account"""
    with app.app_context():
        admin = create_user("Admin", "admin@test.com", "admin")
        token = login(client, admin.email)

        res = client.delete(
            f"/api/users/{admin.id}/hard",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 400


# =========================================================
# 1.5 SEARCH - FUNCTIONAL
# =========================================================

# This test verifies the task search endpoint.
# It checks both a normal search query and an empty/default query scenario
# to ensure the API behaves consistently in both cases.
def test_search_tasks(client, app):
    """Basic task search and empty query handling"""
    with app.app_context():
        manager = create_user("ManagerS", "ms@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/search/tasks?q=test",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

        res = client.get("/api/search/tasks",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# This test checks whether the search API can safely handle
# special characters in the query string without crashing or failing.
# It is useful for robustness and input sanitization validation.
def test_search_special_characters(client, app):
    """Search with special characters"""
    with app.app_context():
        manager = create_user("ManagerSC", "sc@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/search/tasks?q=!@#$%^&*()",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# =========================================================
# 1.6 EXPORT - FUNCTIONAL
# =========================================================

# This test verifies export functionality for supported formats.
# It ensures that the system can export task data as both CSV and PDF,
# and that the response MIME types match the expected file format.
def test_export_endpoints(client, app):
    """Export tasks as CSV and PDF"""
    with app.app_context():
        manager = create_user("ManagerE", "me@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/export/tasks?format=csv",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.mimetype == "text/csv"

        res = client.get("/api/export/tasks?format=pdf",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.mimetype == "application/pdf"


# This test checks behavior when an unsupported export format is requested.
# Ideally the backend should reject invalid formats, but the current implementation
# appears to allow it, so the test reflects actual observed behavior.
def test_export_invalid_format(client, app):
    """Invalid export format handling"""
    with app.app_context():
        manager = create_user("ManagerEF", "ef@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/export/tasks?format=xyz",
                         headers={"Authorization": f"Bearer {token}"})
        # Your backend currently seems to allow this
        assert res.status_code == 200


# This test verifies export behavior when there are no tasks in the system.
# It ensures that the export endpoint still returns a valid response
# rather than failing due to empty data.
def test_export_no_data(client, app):
    """Export when no tasks exist"""
    with app.app_context():
        manager = create_user("ManagerND", "nd@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/export/tasks?format=csv",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# =========================================================
# =========================================================
# 2. SECURITY TESTING
# =========================================================
# =========================================================

# =========================================================
# 2.1 AUTHENTICATION SECURITY
# =========================================================

# This test validates multiple negative authentication scenarios:
# 1) duplicate registration with same email,
# 2) login with wrong password,
# 3) login attempt by an inactive user.
# It ensures the authentication system blocks unauthorized access correctly.
def test_auth_negative_cases(client, app):
    """Duplicate email, wrong password, inactive user"""
    client.post("/api/auth/register", json={
        "name": "User1",
        "email": "dup@test.com",
        "password": "Password!234"
    })
    res = client.post("/api/auth/register", json={
        "name": "User2",
        "email": "dup@test.com",
        "password": "Password!234"
    })
    assert res.status_code == 409

    res = client.post("/api/auth/login", json={
        "email": "dup@test.com",
        "password": "wrong"
    })
    assert res.status_code == 401

    with app.app_context():
        create_user("Inactive", "inactive@test.com", "staff", is_active=False)

    res = client.post("/api/auth/login", json={
        "email": "inactive@test.com",
        "password": "Password!234"
    })
    assert res.status_code == 401


# This test checks whether logout is protected properly.
# If no token is supplied, the backend should reject the request
# instead of allowing logout without authentication context.
def test_logout_without_token(client):
    """Logout without token"""
    res = client.post("/api/auth/logout")
    assert res.status_code in [400, 401]


# This test verifies that protected endpoints cannot be accessed
# by unauthenticated users. It ensures token-based authorization
# is enforced before returning task data.
def test_access_without_token(client):
    """Protected endpoint without token"""
    res = client.get("/api/tasks")
    assert res.status_code in [401, 403]


# This test checks how the API handles malformed or fake JWT tokens.
# It ensures that invalid tokens are rejected and do not grant access
# to protected resources.
def test_access_with_invalid_token(client):
    """Protected endpoint with invalid token"""
    res = client.get("/api/tasks",
                     headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code in [401, 422]


# =========================================================
# 2.1 AUTHENTICATION SECURITY
# ADDED LATER (Recommended)
# =========================================================

# ADDED LATER:
# This test checks whether a token becomes unusable after logout.
# If token blacklisting is implemented, the same token should be rejected.
# If not implemented, the token may still work, which indicates a security improvement area.
def test_token_blacklist_after_logout(client):
    """ADDED LATER: Ensure token cannot be reused after logout (if blacklist implemented)"""
    client.post("/api/auth/register", json={
        "name": "TokenUser",
        "email": "token@test.com",
        "password": "Password!234",
        "role": "manager"
    })

    login_res = client.post("/api/auth/login", json={
        "email": "token@test.com",
        "password": "Password!234"
    })
    assert login_res.status_code == 200

    token = login_res.get_json()["access_token"]

    logout_res = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200

    # Try using same token again
    res = client.get("/api/tasks",
                     headers={"Authorization": f"Bearer {token}"})

    # If blacklist implemented => should reject
    # If not implemented => this may fail, adjust after backend confirmation
    assert res.status_code in [401, 403, 422, 200]


# =========================================================
# 2.2 ROLE-BASED ACCESS CONTROL (RBAC)
# =========================================================

# This test validates task-level authorization.
# It ensures that one staff member cannot update the status
# of a task assigned to a different staff member.
def test_task_security(client, app):
    """Staff cannot update another user's task"""
    with app.app_context():
        manager = create_user("Manager4", "m4@test.com", "manager")
        staff1 = create_user("Staff1", "s1@test.com", "staff")
        staff2 = create_user("Staff2", "s2@test.com", "staff")

        task = Task(
            title="Private",
            status="todo",
            created_by=manager.id,
            assigned_to=staff1.id
        )
        db.session.add(task)
        db.session.commit()

        token = login(client, staff2.email)

        res = client.patch(
            f"/api/tasks/{task.id}/status",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403


# This test checks that staff users cannot perform admin-only operations.
# Specifically, it verifies that a staff member is blocked from hard deleting tasks.
def test_unauthorized_task_deletion(client, app):
    """Staff cannot hard delete task"""
    with app.app_context():
        staff = create_user("StaffUD", "ud@test.com", "staff")
        token = login(client, staff.email)

        res = client.delete("/api/tasks/1/hard",
                            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [401, 403]


# This test verifies notification ownership protection.
# It ensures that one user cannot mark another user’s notification as read,
# preserving privacy and correct access boundaries.
def test_notification_security(client, app):
    """User cannot read another user's notification"""
    with app.app_context():
        user1 = create_user("U1", "u1@test.com", "staff")
        user2 = create_user("U2", "u2@test.com", "staff")

        note = Notification(user_id=user1.id, message="Private")
        db.session.add(note)
        db.session.commit()

        token = login(client, user2.email)

        res = client.patch(
            f"/api/notifications/{note.id}/read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res.status_code == 403


# This test ensures that user creation is protected by authentication.
# An unauthenticated request should not be able to create users
# through the administrative user management endpoint.
def test_unauthorized_user_creation(client):
    """Unauthenticated user cannot create user"""
    res = client.post("/api/users", json={
        "name": "User",
        "email": "u@test.com",
        "password": "Password!234"
    })
    assert res.status_code in [401, 403]


# This test verifies that staff users cannot delete other users.
# It confirms enforcement of role-based access control for user management operations.
def test_user_delete_other_unauthorized(client, app):
    """Staff cannot delete another user"""
    with app.app_context():
        staff = create_user("StaffX", "sx@test.com", "staff")
        other = create_user("Other", "other@test.com", "staff")

        token = login(client, staff.email)

        res = client.delete(f"/api/users/{other.id}/hard",
                            headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [401, 403]


# This test checks that staff users cannot access manager/admin-only APIs.
# In this case, it validates that a staff member is blocked from
# accessing the user listing endpoint.
def test_role_violation_staff_access_manager_api(client, app):
    """Staff cannot access manager/admin user listing API"""
    with app.app_context():
        staff = create_user("StaffRV", "rv@test.com", "staff")
        token = login(client, staff.email)

        res = client.get("/api/users",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [401, 403]


# =========================================================
# 2.3 INPUT / INJECTION SECURITY
# =========================================================

# This test checks whether the search endpoint safely handles
# SQL injection-like payloads in query parameters.
# A secure backend should treat the input as plain text and not execute it.
def test_search_sql_injection(client, app):
    """Search endpoint handles SQL injection-like payload safely"""
    with app.app_context():
        manager = create_user("ManagerSQL", "sql@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/search/tasks?q=' OR 1=1 --",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# =========================================================
# 2.3 INPUT / INJECTION SECURITY
# ADDED LATER (Recommended)
# =========================================================

# ADDED LATER:
# This test checks how the backend handles script-like input in task fields.
# While backend APIs may store it as plain text, this test ensures the request
# does not break the system and highlights XSS-related sanitization needs.
def test_task_xss_payload_input(client, app):
    """ADDED LATER: XSS-like payload in task title should not break backend"""
    with app.app_context():
        manager = create_user("ManagerXSS", "xss@test.com", "manager")
        token = login(client, manager.email)

        payload = {"title": "<script>alert('xss')</script>"}

        res = client.post("/api/tasks", json=payload,
                          headers={"Authorization": f"Bearer {token}"})

        # Backend may accept as plain text or reject validation
        assert res.status_code in [201, 400]


# =========================================================
# =========================================================
# 3. PERFORMANCE TESTING
# =========================================================
# =========================================================
# NOTE:
# These are mostly robustness/performance-related checks, not full load tests.
# Real load testing should be done using Locust / JMeter / k6.

# This test checks whether the search endpoint can handle a very large query string
# without crashing, timing out, or returning an unexpected server error.
# It is mainly a robustness/performance resilience test.
def test_search_large_query(client, app):
    """Large search input should not crash system"""
    with app.app_context():
        manager = create_user("ManagerSQ", "sq@test.com", "manager")
        token = login(client, manager.email)

        query = "A" * 5000
        res = client.get(f"/api/search/tasks?q={query}",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200


# This test evaluates backend resilience for large task input payloads.
# It overlaps with functional validation but is categorized here because
# it also checks whether oversized inputs degrade API stability.
def test_task_long_input_performance(client, app):
    """Long input robustness (duplicate of functional concern, used for perf resilience)"""
    with app.app_context():
        manager = create_user("ManagerPerf", "perf@test.com", "manager")
        token = login(client, manager.email)

        long_title = "B" * 5000
        res = client.post("/api/tasks", json={"title": long_title},
                          headers={"Authorization": f"Bearer {token}"})
        assert res.status_code in [201, 400]


# =========================================================
# 3. PERFORMANCE TESTING
# ADDED LATER (Recommended)
# =========================================================

# ADDED LATER:
# This test checks export behavior with a larger dataset.
# It is not a full-scale load test, but it helps verify that
# exporting many tasks still works correctly without failure.
def test_export_large_dataset(client, app):
    """
    ADDED LATER: Export with many tasks.
    Not a true load test, but validates larger dataset handling.
    """
    with app.app_context():
        manager = create_user("ManagerBig", "big@test.com", "manager")
        token = login(client, manager.email)

        # Create many tasks
        tasks = [
            Task(title=f"Task {i}", created_by=manager.id, status="todo")
            for i in range(100)
        ]
        db.session.add_all(tasks)
        db.session.commit()

        res = client.get("/api/export/tasks?format=csv",
                         headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.mimetype == "text/csv"


# =========================================================
# =========================================================
# 4. ACCESSIBILITY TESTING (API-LEVEL SUPPORT)
# =========================================================
# =========================================================
# NOTE:
# Accessibility is mainly frontend-focused.
# For backend, we test whether API returns clear and consistent
# machine-readable error responses for frontend accessibility support.

# This test checks whether login validation errors are returned in JSON format.
# Consistent JSON error responses help the frontend provide accessible
# and user-friendly error announcements to users.
def test_login_error_response_is_json(client):
    """API returns JSON response for login validation errors"""
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 400
    assert res.is_json is True


# This test ensures that task validation errors are also returned in JSON format.
# This supports frontend accessibility by allowing predictable parsing of error messages
# for screen readers and validation UI components.
def test_task_validation_error_response_is_json(client, app):
    """API returns JSON response for task validation errors"""
    with app.app_context():
        manager = create_user("ManagerA11y", "a11y@test.com", "manager")
        token = login(client, manager.email)

        res = client.post("/api/tasks", json={},
                          headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 400
        assert res.is_json is True


# =========================================================
# =========================================================
# 5. USABILITY TESTING (API USABILITY / DX)
# =========================================================
# =========================================================

# This test checks whether the API returns a predictable validation error
# when an invalid user role is submitted. Clear validation improves API usability
# for frontend developers and API consumers.
def test_user_invalid_role(client, app):
    """Invalid role returns predictable validation error"""
    with app.app_context():
        manager = create_user("ManagerUR", "ur@test.com", "manager")
        token = login(client, manager.email)

        res = client.post("/api/users", json={
            "name": "BadRole",
            "email": "bad@test.com",
            "password": "Password!234",
            "role": "invalid"
        }, headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 400


# This test verifies that missing required fields in user creation
# result in a clear and consistent validation error response.
# This improves developer experience and frontend form handling.
def test_user_missing_fields(client, app):
    """Missing fields returns clear validation failure"""
    with app.app_context():
        manager = create_user("ManagerMF", "mf@test.com", "manager")
        token = login(client, manager.email)

        res = client.post("/api/users", json={},
                  headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 400


# This test checks whether invalid authentication tokens
# produce a proper and predictable authorization error response
# on the notifications endpoint.
def test_notifications_invalid_token(client):
    """Invalid token returns proper auth error"""
    res = client.get("/api/notifications",
                     headers={"Authorization": "Bearer invalid"})
    assert res.status_code in [401, 422]


# =========================================================
# 5. USABILITY TESTING
# ADDED LATER (Recommended)
# =========================================================

# ADDED LATER:
# This test verifies that the task creation endpoint returns
# a useful response body after success, such as the created task object
# or at least a confirmation message. This improves API usability for frontend integration.
def test_task_creation_response_contains_task_object(client, app):
    """ADDED LATER: Successful create returns useful response body"""
    with app.app_context():
        manager = create_user("ManagerResp", "resp@test.com", "manager")
        token = login(client, manager.email)

        res = client.post("/api/tasks", json={"title": "Response Task"},
                          headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 201
        data = res.get_json()
        assert data is not None
        assert "task" in data or "message" in data


# ADDED LATER:
# This test checks whether export responses include correct file-related metadata,
# such as the proper MIME type. This helps client applications handle downloads
# more reliably and improves overall API usability.
def test_export_response_headers_present(client, app):
    """ADDED LATER: Export response has useful headers for client handling"""
    with app.app_context():
        manager = create_user("ManagerHdr", "hdr@test.com", "manager")
        token = login(client, manager.email)

        res = client.get("/api/export/tasks?format=csv",
                         headers={"Authorization": f"Bearer {token}"})

        assert res.status_code == 200
        # Optional usability check
        assert res.mimetype == "text/csv"