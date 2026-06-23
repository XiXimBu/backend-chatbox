from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from helper.import_helper import load_module
from google.genai import errors

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
    except errors.ClientError as e:
        if e.code == 429:
            # Trả về mã 200 bình thường kèm tin nhắn thân thiện để UI vẽ ra bong bóng chat
            return ChatResponse(reply="⚠️ [Hệ thống] Bot đã kiệt sức vì phỏng vấn quá nhiều ứng viên (Hết hạn mức API Google). Vui lòng đợi khoảng 1 phút rồi hẵng chat tiếp nhé!")
        else:
            raise HTTPException(status_code=500, detail=f"Lỗi API Gemini: {e.message}")
            
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
        
    # 3. NẾU LÀ CÁC LỖI KHÁC (NHƯ SẬP DATABASE) THÌ MỚI BÁO 500
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Không thể xử lý tin nhắn: {error}",
        )

    return ChatResponse(reply=reply)
