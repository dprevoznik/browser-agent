from pathlib import Path
from browser_use import Agent, AgentHistoryList
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
    duration: float
    result: str
    files: list[str]
    errors: list[str]

    @classmethod
    def build(cls, session: str, agent: Agent, history: AgentHistoryList):
        files: list[str] = []
        if downloads_path := agent.browser_profile.downloads_path:
            files = [str(path) for path in Path(downloads_path).glob("*")]

        return cls(
            session=session,
            duration=history.total_duration_seconds(),
            result=history.final_result(),
            files=files,
            errors=list(filter(bool, history.errors())),
        )
