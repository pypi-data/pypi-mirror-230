from functools import lru_cache
from typing import Tuple

from fetchfox import rest
from fetchfox.blockchains.cardano import utils

BASE_URL = "https://api.cnft.tools/api"


def get(service: str, params: dict = None) -> Tuple[dict, int]:
    return rest.get(
        url=f"{BASE_URL}/{service}",
        params=params or {},
    )


@lru_cache(maxsize=None)
def get_ranks(policy_id: str) -> dict:
    response, status_code = get(f"rankings/{policy_id}")

    if response.get("error"):
        return None

    return response


@lru_cache(maxsize=None)
def get_rank(asset_id: str) -> int:
    policy_id, asset_name = utils.split_asset_id(asset_id)
    asset_name = asset_name.replace(" ", "").replace("#", "")

    ranks = get_ranks(policy_id)

    if ranks is None:
        return None

    return ranks.get(asset_name)
