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


app = FastAPI(title="AI Chatbox API", lifespan=lifespan)
app.include_router(index_controller.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Cho phép Frontend này truy cập
    allow_credentials=True,
    allow_methods=["*"], # Cho phép mọi method (GET, POST...)
    allow_headers=["*"], # Cho phép mọi header
)

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API của Chatbot!"}
