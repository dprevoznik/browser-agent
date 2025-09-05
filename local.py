import logging
from uuid import uuid4

from kernel import KernelContext
from dotenv import load_dotenv
from fastapi import FastAPI

import main

load_dotenv()

logger = logging.getLogger(__name__)
server = FastAPI(title=main.app.name)

logger.info("Available endpoints:")
logger.info(f"App {server.title}")

for action in main.app.actions.values():
    path = f"/apps/{server.title}/actions/{action.name}"
    logger.info(f"  POST {path}")

    @server.post(path)
    async def handler(params: dict) -> dict:
        ctx = KernelContext(invocation_id=f"local:{uuid4().hex}")
        return await action.handler(ctx, params)
