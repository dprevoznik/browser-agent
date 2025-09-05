from functools import partial
from os import environ as env
import typing as t

from browser_use import ChatGoogle, ChatOpenAI, ChatAnthropic
from browser_use.llm import BaseChatModel
from google.genai.types import HttpOptions

ModelProvider = t.Literal["anthropic", "gemini", "openai"]

AI_GATEWAY_URL = env["AI_GATEWAY_URL"]
DEFAULT_HEADERS = {
    "cf-aig-authorization": env["AI_GATEWAY_TOKEN"],
}


ChatFactory: dict[ModelProvider, t.Callable[[str, str], BaseChatModel]] = {
    "gemini": partial(
        ChatGoogle,
        http_options=HttpOptions(
            base_url=f"{AI_GATEWAY_URL}/google-ai-studio",
            headers=DEFAULT_HEADERS,
        ),
    ),
    "openai": partial(
        ChatOpenAI,
        base_url=f"{AI_GATEWAY_URL}/openai",
        default_headers=DEFAULT_HEADERS,
    ),
    "anthropic": partial(
        ChatAnthropic,
        base_url=f"{AI_GATEWAY_URL}/anthropic",
        default_headers=DEFAULT_HEADERS,
    ),
}

AGENT_INSTRUCTIONS = """Remember, you are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user. Decompose the user's query into all required sub-requests, and confirm that each is completed. Do not stop after completing only part of the request. Only terminate your turn when you are sure that the problem is solved. You must be prepared to answer multiple queries and only finish the call once the user has confirmed they're done.

You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made, ensuring the user's query, and related sub-requests are completely resolved."""
