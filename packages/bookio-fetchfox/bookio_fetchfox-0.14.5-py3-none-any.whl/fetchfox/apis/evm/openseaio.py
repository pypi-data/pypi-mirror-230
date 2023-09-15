import logging
from functools import lru_cache
from typing import Iterable, Tuple

from fetchfox import rest
from fetchfox.checks import check_str

BASE_URL = "https://api.opensea.io"

logger = logging.getLogger(__name__)


def get(service: str, api_key: str, params: dict = None, version: int = 2, check: str = None) -> Tuple[dict, int]:
    check_str(api_key, "openseaio.api_key")

    if version == 1:
        url = f"{BASE_URL}/api/v{version}/{service}"
    else:
        url = f"{BASE_URL}/v{version}/{service}"

    return rest.get(
        url=url,
        headers={
            "X-API-KEY": api_key,
        },
        params=params or {},
        sleep=2.5,
    )


@lru_cache(maxsize=None)
def get_slug(contract_address: str, api_key) -> str:
    check_str(contract_address, "openseaio.contract_address")
    contract_address = contract_address.strip().lower()

    logger.info("fetching slug for %s", contract_address)

    response, status_code = get(
        "events",
        params={
            "asset_contract_address": contract_address,
            "token_id": 0,
            "event_type": "transfer",
        },
        version=1,
        api_key=api_key,
    )

    return response["asset_events"][0]["collection_slug"]


def get_events(contract_address: str, event_type: str, api_key: str, slug: str = None) -> Iterable[dict]:
    contract_address = contract_address.strip().lower()

    if not slug:
        slug = get_slug(contract_address, api_key=api_key)

    cursor = ""

    while True:
        response, status_code = get(
            "events",
            params={
                "collection_slug": slug,
                "only_opensea": "true",
                "event_type": event_type,
                "cursor": cursor,
            },
            version=1,
            api_key=api_key,
        )

        yield from response["asset_events"]

        cursor = response["next"]

        if not cursor:
            break


def get_sales(contract_address: str, api_key: str, slug: str = None) -> Iterable[dict]:
    yield from get_events(
        contract_address,
        event_type="successful",
        api_key=api_key,
        slug=slug,
    )


def get_listings(contract_address: str, api_key: str, slug: str = None) -> Iterable[dict]:
    contract_address = contract_address.strip().lower()

    if not slug:
        slug = get_slug(contract_address, api_key=api_key)

    cursor = ""

    while True:
        response, status_code = get(
            f"listings/collection/{slug}/all",
            params={
                "next": cursor,
            },
            api_key=api_key,
        )

        yield from response.get("listings", [])

        cursor = response.get("next")

        if not cursor:
            break
