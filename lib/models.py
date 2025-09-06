import typing as t

from browser_use.agent.views import AgentHistoryList
from pydantic import BaseModel

from lib.ai import ModelProvider


class BrowserAgentRequest(BaseModel):
    # Request Definition
    instructions: str = ""
    input: str
    provider: ModelProvider
    model: str
    api_key: str
    # Browser Config
    stealth: bool = True
    headless: bool = False
    browser_timeout: int = 60
    # Browser Use Config
    max_steps: int = 100
    reasoning: bool = True
    flash: bool = False


class BrowserAgentResponse(BaseModel):
    session: str
    success: bool
    duration: float
    result: str
    downloads: dict[str, str]

    @classmethod
    def from_run(
        cls,
        run: AgentHistoryList,
        **kwargs,
    ) -> t.Self:
        return cls(
            success=run.is_successful(),
            duration=run.total_duration_seconds(),
            result=run.final_result(),
            **kwargs,
        )
