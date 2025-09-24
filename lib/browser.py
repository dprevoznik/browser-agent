import logging
from os import environ as env, getenv

from browser_use import BrowserProfile, Browser
from kernel import AsyncKernel, KernelContext
from kernel.types import BrowserCreateParams
import anyio
import orjson

from lib.models import BrowserAgentRequest

VIEWPORT_SIZE = orjson.loads(getenv("VIEWPORT_SIZE", '{"width": 1440, "height": 900}'))

kernel = AsyncKernel(api_key=env["KERNEL_API_KEY"])
logger = logging.getLogger(__name__)


DOWNLOADS_PATH = anyio.Path(getenv("DOWNLOADS_PATH", "/tmp/downloads"))


async def create(ctx: KernelContext, request: BrowserAgentRequest):
    invocation_id = ctx.invocation_id
    headless = request.headless

    remote_browser_params: BrowserCreateParams = {
        "headless": headless,
        "stealth": request.stealth,
    }
    if not invocation_id.startswith("local:"):
        remote_browser_params["invocation_id"] = invocation_id

    remote_browser = await kernel.browsers.create(**remote_browser_params)

    session = remote_browser.session_id
    logger.info(f"Created browser session: {session}")
    if not headless:
        logger.info(f"Browser live view: {remote_browser.browser_live_view_url}")

    browser = Browser(
        id=invocation_id,
        browser_profile=BrowserProfile(
            is_local=False,
            cdp_url=remote_browser.cdp_ws_url,
            headless=headless,
            screen=VIEWPORT_SIZE,
            viewport=VIEWPORT_SIZE,
            downloads_path=str(DOWNLOADS_PATH),
            auto_download_pdfs=True,
        ),
    )

    return session, browser, DOWNLOADS_PATH
