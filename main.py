from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helper.import_helper import load_module

index_controller = load_module("index_controller", "controller", "index.controller.py")
database = load_module("database", "config", "database.py")


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


app = FastAPI(title="AI Chatbox API", lifespan=lifespan)
app.include_router(index_controller.router)
raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Cho phép Frontend này truy cập
    allow_credentials=True,
    allow_methods=["*"], # Cho phép mọi method (GET, POST...)
    allow_headers=["*"], # Cho phép mọi header
)

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API của Chatbot!"}
