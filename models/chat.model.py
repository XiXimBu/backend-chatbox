from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password: str = Field(default="")

    messages: List["ChatMessage"] = Relationship(back_populates="user")


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: str = Field(primary_key=True)
    level: str = Field(default="basic")
    topic: str = Field(default="python")

    messages: List["ChatMessage"] = Relationship(back_populates="chat_session")


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="chat_sessions.id", index=True)
    role: str
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")

    user: Optional[User] = Relationship(back_populates="messages")
    chat_session: Optional[ChatSession] = Relationship(back_populates="messages")
