import asyncio
import logging

from browser_use import Agent
from kernel import App, KernelContext
from zenbase_llml import llml

from lib.ai import AGENT_INSTRUCTIONS, ChatFactory
from lib.browser import DOWNLOADS_PATH, create_browser
from lib.models import BrowserAgentRequest, BrowserAgentResponse
from lib.storage import upload_files, upload_json

logger = logging.getLogger(__name__)

app = App("browser-agent")


@app.action("perform")
async def perform(ctx: KernelContext, params: dict):
    request = BrowserAgentRequest.model_validate(params)

    llm = ChatFactory[request.provider](
        api_key=request.api_key,
        model=request.model,
    )

    session, browser = await create_browser(ctx, request)

    prompt = {
        "instructions": "\n\n".join(
            filter(bool, [request.instructions, AGENT_INSTRUCTIONS])
        ),
        "input": request.input,
    }

    agent = Agent(
        task=llml(prompt),
        browser=browser,
        llm=llm,
        use_thinking=request.reasoning,
        flash_mode=request.flash,
    )

    trajectory = await agent.run(max_steps=request.max_steps)

    uploads = await asyncio.gather(
        upload_files(dir=session, files=DOWNLOADS_PATH.glob("*")),
        upload_json(trajectory.model_dump(), key=f"{session}/trajectory.json"),
    )

    response = BrowserAgentResponse.from_run(
        trajectory,
        session=session,
        downloads=uploads[0],
    )
    return response.model_dump()
