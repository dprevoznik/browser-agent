import logging

from browser_use import Agent
from kernel import App, AsyncKernel, KernelContext
from sorcery import dict_of

from lib.browser.models import BrowserAgentRequest
from lib.browser.session import CustomBrowserSession

kernel = AsyncKernel()
app = App("browser-agent")

logger = logging.getLogger(__name__)


@app.action("browser-agent")
async def browser_agent(ctx: KernelContext, input_data: dict):
    request = BrowserAgentRequest(**input_data)
    browser = await kernel.browsers.create(
        invocation_id=ctx.invocation_id,
        stealth=True,
        headless=False,
        timeout=60,
    )
    logger.info(f"Created browser [live view: {browser.browser_live_view_url}]")

    agent = Agent(
        task=request.task,
        llm=request.llm,
        browser_session=CustomBrowserSession(cdp_url=browser.cdp_ws_url),
    )

    trajectory = await agent.run()

    duration = trajectory.total_duration_seconds
    errors = trajectory.errors()
    result = trajectory.final_result()
    downloads = agent.browser_session.downloaded_files

    if not result:
        return dict_of(duration, errors)

    return dict_of(duration, result, downloads)
