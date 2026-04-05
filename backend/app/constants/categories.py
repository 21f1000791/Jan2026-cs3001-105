DEFAULT_TASK_CATEGORIES = [
    "Maintenance",
    "Construction",
    "Electrical",
    "Sanitation",
    "Landscaping",
]


def normalize_category(value):
    raw = str(value or "").strip()
    if not raw:
        return None

    match = {item.lower(): item for item in DEFAULT_TASK_CATEGORIES}.get(raw.lower())
    return match