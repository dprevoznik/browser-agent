import logging

from browser_use import Agent
from kernel import App, KernelContext
from zenbase_llml import llml

from lib.ai import AGENT_INSTRUCTIONS, ChatFactory
from lib.browser import create_browser
from lib.models import BrowserAgentRequest, BrowserAgentResponse

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
        "notes": """
        Your browser will automatically:
        1. Download the PDF file upon viewing it. Just wait for it.
        2. Solve CAPTCHAs or similar tests. Just wait for it.
        """,
    }

    agent = Agent(
        task=llml(prompt),
        browser=browser,
        llm=llm,
        use_thinking=request.reasoning,
        flash_mode=request.flash,
    )

    history = await agent.run(max_steps=request.max_steps)

    response = BrowserAgentResponse.build(session, agent, history)
    return response.model_dump()
