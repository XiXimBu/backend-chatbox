import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from helper.import_helper import load_module

load_dotenv()

MODEL = "gemini-2.5-flash"
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


def create_chat_session(level: str, topic: str, history=None):
    client = get_client()
    return client.chats.create(
        model=MODEL,
        config=get_chat_config(level, topic),
        history=history,
    )
