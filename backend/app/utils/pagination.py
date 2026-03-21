def parse_pagination_args(args, default_page=1, default_page_size=20, max_page_size=100):
    try:
        page = int(args.get("page", default_page))
    except (TypeError, ValueError):
        page = default_page

    try:
        per_page = int(args.get("per_page", default_page_size))
    except (TypeError, ValueError):
        per_page = default_page_size

    page = max(1, page)
    per_page = max(1, min(per_page, max_page_size))
    return page, per_page


def build_pagination_meta(pagination):
    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }
