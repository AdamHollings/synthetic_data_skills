import asyncio
import os
import time
from contextvars import ContextVar

from dotenv import load_dotenv
from openai import OpenAI

# FOUNDRY SPECIFIC IMPORTS

from foundry_sdk.v2.language_models.utils import get_openai_base_url, get_http_client
from foundry_sdk._core.context_and_environment_vars import HOSTNAME_VAR, TOKEN_VAR

load_dotenv()

_loop_semaphore: ContextVar[asyncio.Semaphore] = ContextVar("_loop_semaphore", default=None)

# FOUNDRY SPECIFIC FUNCTIONS

# 1 - call_llm

def call_llm(prompt: str, model: str = "ri.language-model-service..language-model.gpt-5-1", temp: float = 0.7, max_attempts: int = 5, chat_history = None, verbose: bool = False) -> str:
    """
    Send a prompt to a chat-based LLM and return the model's text response.

    Builds a chat completion request using the provided prompt and optional
    conversation history, calls the model, and returns the raw response text.
    If the request fails, it retries up to `max_attempts` times.

    Parameters
    ----------
    prompt : str
        The user prompt appended as the latest message in the conversation.

    model : object
        Model client implementing `create_chat_completion(request)`.

    temp : float, default=0.7
        Sampling temperature controlling response randomness.

    max_attempts : int, default=3
        Number of retry attempts if the LLM call fails.

    chat_history : list[str] | None, default=None
        Optional alternating list of messages:
        [user_0, assistant_0, user_1, assistant_1, ...].
        The prompt is added as the final user message.

    Returns
    -------
    str
        Raw text content from the model response, or None if all attempts fail.
    """
    HOSTNAME_VAR.set(os.getenv("FOUNDRY_HOSTNAME"))
    TOKEN_VAR.set(os.getenv("TOKEN") or os.getenv("FOUNDRY_TOKEN"))
    token = os.getenv("TOKEN") or os.getenv("FOUNDRY_TOKEN")
    client = OpenAI(
        api_key=token,
        base_url=get_openai_base_url(preview=True),
        http_client=get_http_client(preview=True),
    )

    if not chat_history:
        messages = [{"role": "user", "content": prompt}]
    else:
        messages = [
            {"role": "user" if i % 2 == 0 else "assistant", "content": chat_history[i]}
            for i in range(len(chat_history))
        ]
        messages.append({"role": "user", "content": prompt})

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
            )
            return str(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM call failed with error: {e} on attempt {attempt + 1}/{max_attempts}. Retrying...")
            time.sleep( (attempt+1)**2 *10)

    print(f"Failed after {max_attempts} attempts.")
    return None

async def call_llm_async(prompt: str, model="ri.language-model-service..language-model.gpt-5-1", temp: float = 0.7, max_attempts: int = 5, chat_history=None, verbose: bool = False):
    """
    Async wrapper for the synchronous LLM call, limited to 'llm_semaphore' concurrent calls.
    """
    sem = _loop_semaphore.get()
    if sem is None:
        sem = asyncio.Semaphore(1)
        _loop_semaphore.set(sem)

    async with sem:
        return await asyncio.to_thread(
            call_llm, prompt, model, temp, max_attempts, chat_history, verbose
        )