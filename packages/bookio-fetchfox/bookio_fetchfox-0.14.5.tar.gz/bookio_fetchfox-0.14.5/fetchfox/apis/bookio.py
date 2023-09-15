from typing import Iterable

from fetchfox import rest

BASE_URL = "https://api.book.io"


def campaigns() -> Iterable[dict]:
    response, status_code = rest.get(
        f"{BASE_URL}/treasury/campaigns/all",
    )

    yield from response.get("campaigns", [])
