import logging
from pathlib import Path
from os import environ as env

from browser_use import Agent, BrowserProfile
from kernel import AsyncKernel, KernelContext
from kernel.types import BrowserCreateParams

from lib.models import BrowserAgentRequest
from lib.patch import PatchedBrowser

VIEWPORT_SIZE = {"width": 1280, "height": 800}

kernel = AsyncKernel(api_key=env["KERNEL_API_KEY"])
logger = logging.getLogger(__name__)


def downloaded_files(agent: Agent) -> list[Path]:
    if downloads_path := agent.browser_profile.downloads_path:
        return list(Path(downloads_path).glob("*"))
    return []


async def create_browser(ctx: KernelContext, request: BrowserAgentRequest):
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

    browser = PatchedBrowser(
        id=invocation_id,
        browser_profile=BrowserProfile(
            is_local=False,
            cdp_url=remote_browser.cdp_ws_url,
            headless=headless,
            screen=VIEWPORT_SIZE,
            viewport=VIEWPORT_SIZE,
            downloads_path="/tmp/downloads",
            auto_download_pdfs=True,
        ),
    )

    return session, browser
