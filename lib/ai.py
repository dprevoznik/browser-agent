from functools import partial
from os import getenv
import typing as t

from browser_use import (
    ChatGoogle,
    ChatOpenAI,
    ChatAnthropic,
    ChatAzureOpenAI,
    ChatGroq,
    ChatOllama,
)
from browser_use.llm import BaseChatModel
import orjson

__all__ = ["ModelProvider", "ChatFactory", "AGENT_INSTRUCTIONS"]


ModelProvider = t.Literal[
    "anthropic", "gemini", "openai", "azure_openai", "groq", "ollama"
]


def config(provider: ModelProvider) -> dict:
    return orjson.loads(getenv(f"{provider.upper()}_CONFIG", "{}"))


ChatFactory: dict[ModelProvider, t.Callable[[str, str], BaseChatModel]] = {
    "gemini": partial(ChatGoogle, **config("gemini")),
    "openai": partial(ChatOpenAI, **config("openai")),
    "anthropic": partial(ChatAnthropic, **config("anthropic")),
    "azure-openai": partial(ChatAzureOpenAI, **config("azure_openai")),
    "groq": partial(ChatGroq, **config("groq")),
    "ollama": partial(ChatOllama, **config("ollama")),
}


AGENT_INSTRUCTIONS = """Remember, you are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Decompose the user's query into all required sub-requests, and confirm that each is completed. Do not stop after completing only part of the request. Only terminate your turn when you are sure that the problem is solved. You must be prepared to answer multiple queries and only finish the call once the user has confirmed they're done.

You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ensuring the user's query, and related sub-requests are completely resolved.

Note that your browser will automatically:
1. Download the PDF file upon viewing it. Just wait for it. You do not need to read the PDF.
2. Solve CAPTCHAs or similar tests. Just wait for it."""
