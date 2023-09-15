import logging
import time

from cachetools.func import ttl_cache

from fetchfox import rest
from fetchfox.constants.currencies import ALGO, ADA, ETH, MATIC

logger = logging.getLogger(__name__)

IDS = {
    ALGO: "algorand",
    ADA: "cardano",
    ETH: "ethereum",
    MATIC: "matic-network",
}


@ttl_cache(ttl=5 * 60)
def usd(currency: str):
    time.sleep(5)

    currency = currency.strip().upper()

    id = IDS[currency]

    logger.info("fetching exchange for %s (%s)", currency, id)

    response, status_code = rest.get(
        url="https://api.coingecko.com/api/v3/simple/price",
        params={
            "ids": id,
            "vs_currencies": "usd",
        },
    )

    return response[id]["usd"]
