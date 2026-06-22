from fastapi import APIRouter
from helper.import_helper import load_module

chat_controller = load_module("chat_controller", "controller", "chat.controller.py")
user_controller = load_module("user_controller", "controller", "user.controller.py")

router = APIRouter()
router.include_router(chat_controller.router)
router.include_router(user_controller.router)
