import typing as t

from browser_use import ChatAnthropic, ChatGoogle, ChatOpenAI
from browser_use.llm.base import BaseChatModel
from pydantic import BaseModel
from zenbase_llml import llml

from lib.gateway import AI_GATEWAY_TOKEN, AI_GATEWAY_URL


ModelProvider = t.Literal["anthropic", "gemini", "openai"]


class BrowserAgentRequest(BaseModel):
    url: str
    instructions: str = ""
    input: str
    provider: ModelProvider
    model: str
    api_key: str
    max_steps: int = 100

    @property
    def base_url(self) -> str:
        path = {"gemini": "google-ai-studio"}.get(self.provider) or self.provider
        return f"{AI_GATEWAY_URL}/{path}"

    @property
    def llm(self) -> BaseChatModel:
        ChatModel = {
            "anthropic": ChatAnthropic,
            "gemini": ChatGoogle,
            "openai": ChatOpenAI,
        }[self.provider]

        return ChatModel(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "cf-aig-authorization": AI_GATEWAY_TOKEN,
            },
        )

    @property
    def task(self) -> str:
        instructions: list[str] = []

        if self.instructions:
            instructions.append(self.instructions.strip())

        instructions.append(
            "If you see a CAPTCHA or similar test, just wait for it to get solved automatically by the browser."
        )

        return llml({"instructions": "\n\n".join(instructions), "input": self.input})
