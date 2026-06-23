from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from google.genai import errors

from helper.import_helper import load_module

chat_service_mod = load_module("chat_service", "services", "chat.service.py")

router = APIRouter(prefix="/api", tags=["chat"])

BUSY_REPLY = (
    "⚠️ [Hệ thống] Model AI đang quá tải tạm thời (Google Gemini 503). "
    "Vui lòng đợi 30–60 giây rồi gửi lại tin nhắn."
)
RATE_LIMIT_REPLY = (
    "⚠️ [Hệ thống] Đã vượt hạn mức API Google (429). "
    "Vui lòng đợi khoảng 1 phút rồi thử lại."
)


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
    except errors.ClientError as error:
        if error.code == 429:
            return ChatResponse(reply=RATE_LIMIT_REPLY)
        raise HTTPException(status_code=400, detail=f"Lỗi API Gemini: {error.message}")
    except errors.ServerError as error:
        if error.code in {503, 502, 504}:
            return ChatResponse(reply=BUSY_REPLY)
        raise HTTPException(status_code=502, detail=f"Lỗi server Gemini: {error.message}")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể xử lý tin nhắn: {error}",
        )

    return ChatResponse(reply=reply)
