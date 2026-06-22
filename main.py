import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from helper.import_helper import load_module

index_controller = load_module("index_controller", "controller", "index.controller.py")
database = load_module("database", "config", "database.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

# 1. Khởi tạo App
app = FastAPI(title="AI Chatbox API", lifespan=lifespan)

# 2. Chuẩn bị danh sách Domain
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in raw_origins.split(",")]

# 3. KÍCH HOẠT MIDDLEWARE BẢO VỆ TRƯỚC!
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# 4. SAU ĐÓ MỚI GẮN ROUTER VÀO SAU BỨC TƯỜNG BẢO VỆ
app.include_router(index_controller.router)

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API của Chatbot!"}