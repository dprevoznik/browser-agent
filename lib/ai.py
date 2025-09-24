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

__all__ = ["ModelProvider", "ChatFactory"]


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
