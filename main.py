import asyncio
import logging

from browser_use import Agent
from kernel import App, KernelContext
from zenbase_llml import llml

from lib import storage, ai, browser, models

logger = logging.getLogger(__name__)

app = App("browser-agent")


@app.action("perform")
async def perform(ctx: KernelContext, params: dict):
    request = models.BrowserAgentRequest.model_validate(params)

    llm = ai.ChatFactory[request.provider](
        api_key=request.api_key,
        model=request.model,
    )

    instructions = f"""
    You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Decompose the user's query into all required sub-requests, and confirm that each is completed. Do not stop after completing only part of the request. Only terminate your turn when you are sure that the problem is solved. You must be prepared to answer multiple queries and only finish the call once the user has confirmed they're done.

    You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ensuring the user's query, and related sub-requests are completely resolved.

    {request.instructions}

    Remember, you are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Decompose the user's query into all required sub-requests, and confirm that each is completed. Do not stop after completing only part of the request. Only terminate your turn when you are sure that the problem is solved. You must be prepared to answer multiple queries and only finish the call once the user has confirmed they're done.

    You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ensuring the user's query, and related sub-requests are completely resolved.

    Note that your browser will automatically:
    1. Download the PDF file upon viewing it. Just wait for it. You do not need to read the PDF.
    2. Solve CAPTCHAs or similar tests. Just wait for it.
    """

    session_id, browser_session, downloads_path = await browser.create(ctx, request)
    agent = Agent(
        task=llml({"instructions": instructions, "input": request.input}),
        browser=browser_session,
        llm=llm,
        use_thinking=request.reasoning,
        flash_mode=request.flash,
    )
    trajectory = await agent.run(max_steps=request.max_steps)

    if not storage.ENABLED:
        downloads = {p.name: str(p) async for p in downloads_path.glob("*")}
    else:
        (downloads,) = await asyncio.gather(
            storage.upload_files(dir=session_id, paths=downloads_path.glob("*")),
            storage.upload_json(
                trajectory.model_dump(),
                key=f"{session_id}/trajectory.json",
            ),
        )

    response = models.BrowserAgentResponse.from_run(
        trajectory,
        session=session_id,
        downloads=downloads,
    )
    return response.model_dump()
