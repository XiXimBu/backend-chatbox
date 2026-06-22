from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from helper.import_helper import load_module

chat_service_mod = load_module("chat_service", "services", "chat.service.py")

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    level: str = "basic"
    topic: str = "python"


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    try:
        reply = chat_service_mod.chat_service.send_message(
            request.user_id,
            request.message,
            request.level,
            request.topic,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể xử lý tin nhắn: {error}",
        )

    return ChatResponse(reply=reply)
