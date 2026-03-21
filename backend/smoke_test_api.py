import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000/api"


def call(method, path, data=None, token=None):
    req = urllib.request.Request(f"{BASE}{path}", method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    payload = json.dumps(data).encode("utf-8") if data is not None else None

    try:
        with urllib.request.urlopen(req, payload, timeout=15) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8")
        try:
            parsed = json.loads(body) if body else {}
        except json.JSONDecodeError:
            parsed = {"raw": body}
        return error.code, parsed


results = []
manager_email = "smoke.manager@example.com"
staff_email = "smoke.staff@example.com"

status, body = call("GET", "/health")
results.append(("health", status, body))

status, body = call(
    "POST",
    "/auth/register",
    {
        "name": "Manager One",
        "email": manager_email,
        "password": "password123",
        "role": "manager",
    },
)
results.append(("register_manager", status, body))

manager_token = body.get("access_token") if isinstance(body, dict) else None

status, body = call(
    "POST",
    "/auth/login",
    {"email": manager_email, "password": "password123"},
)
results.append(("login_manager", status, body))
manager_token = body.get("access_token") or manager_token

status, body = call("GET", "/users", token=manager_token)
results.append(("users_list", status, body))

status, body = call(
    "POST",
    "/users",
    {
        "name": "Staff One",
        "email": staff_email,
        "password": "password123",
        "role": "staff",
    },
    token=manager_token,
)
results.append(("users_create", status, body))

staff_user_id = None
created_user = results[4][2].get("user") if isinstance(results[4][2], dict) else None
if isinstance(created_user, dict):
    staff_user_id = created_user.get("id")

if staff_user_id:
    status, body = call(
        "PUT",
        f"/users/{staff_user_id}",
        {"name": "Staff One Updated", "role": "staff"},
        token=manager_token,
    )
    results.append(("users_update", status, body))

    status, body = call("PUT", f"/users/{staff_user_id}/terminate", token=manager_token)
    results.append(("users_terminate", status, body))

    status, body = call("PUT", f"/users/{staff_user_id}/activate", token=manager_token)
    results.append(("users_activate", status, body))

manager_user_id = None
users_payload = results[3][2]
if isinstance(users_payload, dict):
    items = users_payload.get("items") or []
    if items:
        manager_user_id = items[0].get("id")

status, body = call(
    "POST",
    "/tasks",
    {
        "title": "Integration smoke task",
        "description": "verify API integration",
        "category": "Development",
        "priority": "high",
        "status": "todo",
        "assigned_to": manager_user_id,
    },
    token=manager_token,
)
results.append(("task_create", status, body))

task_id = None
created_task = results[-1][2].get("task") if isinstance(results[-1][2], dict) else None
if isinstance(created_task, dict):
    task_id = created_task.get("id")

if task_id:
    status, body = call(
        "PUT",
        f"/tasks/{task_id}",
        {
            "description": {
                "en": "verify API integration updated",
                "hi": "API एकीकरण सत्यापित करें",
                "kn": "API ಏಕೀಕರಣ ಪರಿಶೀಲಿಸಿ",
            },
            "due_date": "2026-03-20",
            "multilingual_enabled": True,
        },
        token=manager_token,
    )
    results.append(("task_update_with_dict_description", status, body))

status, body = call("GET", "/tasks", token=manager_token)
results.append(("tasks_list", status, body))

for name, status_code, payload in results:
    print(f"[{name}] status={status_code}")
    print(json.dumps(payload, indent=2)[:1200])
    print("---")
