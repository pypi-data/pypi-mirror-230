import logging

from rich.logging import RichHandler

import httpx_cache

logging.basicConfig(
    level="DEBUG", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger("httpx_cache.example")

with httpx_cache.Client(
    base_url="https://httpbin.org/",
    cache=httpx_cache.DictCache(serializer=httpx_cache.DictSerializer()),
) as client:
    logger.info("Running first request ...")
    resp1 = client.get("/get", params={"num": "1"})
    logger.info("Running second request ...")
    resp2 = client.get("/get", params={"num": "1"})
