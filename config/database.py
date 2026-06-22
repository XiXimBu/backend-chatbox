import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được cấu hình trong file .env")

engine = create_engine(DATABASE_URL, echo=False,pool_pre_ping=True)


def init_db():
    from helper.import_helper import load_module

    load_module("chat_model", "models", "chat.model.py")
    SQLModel.metadata.create_all(engine)

    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR NOT NULL DEFAULT ''"
            )
        )


def get_session():
    with Session(engine) as session:
        yield session


