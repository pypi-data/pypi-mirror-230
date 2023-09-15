import asyncio
import logging

import httpx

from contact_magic.conf.settings import SETTINGS
from contact_magic.dict_utils import get_first_level_items
from contact_magic.logger import logger
from contact_magic.utils import fix_website

logging.getLogger("httpx").setLevel(logging.WARNING)

base_url = "https://salesscrapers.dev/api/"


async def make_sales_scraper_request(endpoint, data: dict, max_retries=3):
    if not SETTINGS.SALES_SCRAPERS_API_KEY:
        return None
    headers = {
        "Accept": "application/json",
        "X-API-Key": SETTINGS.SALES_SCRAPERS_API_KEY,
    }

    url = f"{base_url}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as session:
            retries = 0
            params = get_first_level_items(data)
            while retries < max_retries:
                res = await session.request(
                    method="get", url=url, headers=headers, params=params
                )
                # authorization error so can break
                if res.status_code == 401:
                    logger.warning("sales_scraper_error", message=res.text)
                    break
                if res.status_code == 400:
                    logger.warning("proxy_error", message=res.text)
                if res.status_code == 200:
                    return res.json()
                if res.status_code == 422:
                    validation_errors = res.json().get("detail")
                    for error in validation_errors:
                        if error.get("type") == "value_error.url.scheme":
                            error_key = error.get("loc")[1]
                            if error_key in data:
                                params[error_key] = fix_website(data[error_key])
                await asyncio.sleep(30)
                retries += 1
            return None
    except Exception:
        return None
