import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from helper.import_helper import load_module

load_dotenv()

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_MODELS = [
    m.strip()
    for m in os.getenv(
        "GEMINI_FALLBACK_MODELS",
        "gemini-2.0-flash,gemini-2.0-flash-lite",
    ).split(",")
    if m.strip()
]
RETRYABLE_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3

prompt_core = load_module("prompt_core", "core", "promt.core.py")

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY chưa được cấu hình trong file .env")
        _client = genai.Client(api_key=api_key)
    return _client


def get_chat_config(level: str, topic: str) -> types.GenerateContentConfig:
    persona = prompt_core.PersonaFactory.create_persona(level, topic)
    return types.GenerateContentConfig(
        system_instruction=persona.get_system_prompt(),
        temperature=0.7,
    )


def build_gemini_history(messages: list) -> list[dict]:
    history = []
    for msg in messages:
        role = "model" if msg.role == "assistant" else msg.role
        history.append({"role": role, "parts": [{"text": msg.content}]})
    return history


def create_chat_session(level: str, topic: str, history=None, model: str | None = None):
    client = get_client()
    return client.chats.create(
        model=model or DEFAULT_MODEL,
        config=get_chat_config(level, topic),
        history=history,
    )


def _is_retryable(error: errors.APIError) -> bool:
    return error.code in RETRYABLE_CODES


def send_message(level: str, topic: str, history, message: str) -> str:
    models = [DEFAULT_MODEL, *FALLBACK_MODELS]
    seen: set[str] = set()
    last_error: errors.APIError | None = None

    for model in models:
        if model in seen:
            continue
        seen.add(model)

        chat = create_chat_session(level, topic, history, model=model)

        for attempt in range(MAX_RETRIES):
            try:
                response = chat.send_message(message)
                return response.text
            except errors.APIError as error:
                last_error = error
                if not _is_retryable(error):
                    raise
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2**attempt)
                    continue
                break

    if last_error and last_error.code == 503:
        raise errors.ServerError(
            503,
            {
                "message": (
                    "Model Gemini đang quá tải. Vui lòng thử lại sau 30–60 giây."
                ),
                "status": "UNAVAILABLE",
            },
            None,
        )

    if last_error:
        raise last_error

    raise RuntimeError("Không thể gọi Gemini API")
