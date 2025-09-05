import logging

from browser_use import Agent
from kernel import App, AsyncKernel, KernelContext
from sorcery import dict_of

from lib.browser.models import BrowserAgentRequest
from lib.browser.session import CustomBrowserSession

kernel = AsyncKernel()
app = App("browser-agent")

logger = logging.getLogger(__name__)


@app.action("perform")
async def perform(ctx: KernelContext, params: dict):
    request = BrowserAgentRequest.model_validate(params)
    browser = await kernel.browsers.create(
        invocation_id=ctx.invocation_id,
        stealth=True,
        headless=False,
        timeout=60,
    )
    logger.info(f"Created browser {browser.browser_live_view_url}")

    agent = Agent(
        task=request.task,
        llm=request.llm,
        browser_session=CustomBrowserSession(cdp_url=browser.cdp_ws_url),
    )

    trajectory = await agent.run(max_steps=request.max_steps)
    duration = trajectory.total_duration_seconds

    if result := trajectory.final_result():
        files = agent.browser_session.downloaded_files
        return dict_of(duration, result, files)

    errors = trajectory.errors()
    return dict_of(duration, errors)
