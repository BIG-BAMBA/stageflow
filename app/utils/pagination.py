from typing import Any


def paginate(items: list[Any], page: int = 1, size: int = 20) -> dict[str, Any]:
    start = (page - 1) * size
    end = start + size
    return {"items": items[start:end], "page": page, "size": size}
