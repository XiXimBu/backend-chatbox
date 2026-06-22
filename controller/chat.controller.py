from fastapi import APIRouter
from pydantic import BaseModel

from helper.import_helper import load_module

chat_service_mod = load_module("chat_service", "services", "chat.service.py")

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    level: str = "basic"
    topic: str = "python"

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    reply = chat_service_mod.chat_service.send_message(
        request.user_id,
        request.message,
        request.level,
        request.topic,
    )
    return ChatResponse(reply=reply)
