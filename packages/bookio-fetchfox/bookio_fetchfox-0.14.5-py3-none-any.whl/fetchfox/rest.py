import asyncio
import logging
from typing import Tuple

import aiohttp
import backoff
from aiohttp.client_exceptions import ContentTypeError

logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.expo, exception=Exception, max_time=60)
def get(url: str, headers: dict = None, params: dict = None, sleep: float = 0.05, timeout: float = None) -> Tuple[dict, int]:
    async def aux():
        client = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout),
        )

        await asyncio.sleep(sleep)

        async with client as session:
            async with session.get(url, headers=headers, params=params) as response:
                status_code = response.status

                try:
                    json = await response.json()
                except ContentTypeError:
                    json = None

            await response.release()

        if status_code == 429:
            if "Retry-After" in response.headers:  # opensea.io
                wait = int(response.headers["Retry-After"]) + 5
                logger.info("too many requests, waiting for %ss", wait)
                await asyncio.sleep(wait)
                response.raise_for_status()
            elif json.get("detail") == "Request was throttled.":  # opensea.io
                wait = 90
            else:
                wait = 30

            logger.info("too many requests, waiting for %ss", wait)
            await asyncio.sleep(wait)
            response.raise_for_status()

        return json, status_code

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(aux())
    loop.close()

    return result


@backoff.on_exception(backoff.expo, exception=Exception, max_time=60)
def post(url: str, body: dict = None, headers: dict = None, params: dict = None, sleep: float = 0.05, timeout: float = None) -> Tuple[dict, int]:
    async def aux():
        client = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout),
        )

        await asyncio.sleep(sleep)

        async with client as session:
            async with session.post(url, json=body, headers=headers, params=params) as response:
                status_code = response.status

                try:
                    json = await response.json()
                except ContentTypeError:
                    json = None

                await response.release()

            if status_code == 429:
                if "Retry-After" in response.headers:  # opensea.io
                    wait = int(response.headers["Retry-After"]) + 5
                    logger.info("too many requests, waiting for %ss", wait)
                    await asyncio.sleep(wait)
                    response.raise_for_status()
                elif json.get("detail") == "Request was throttled.":  # opensea.io
                    wait = 90
                else:
                    wait = 30

                logger.info("too many requests, waiting for %ss", wait)
                await asyncio.sleep(wait)
                response.raise_for_status()

            return json, status_code

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(aux())
    loop.close()

    return result
