from sqlmodel import Session, delete, select

from helper.import_helper import load_module

db = load_module("database", "config", "database.py")
chat_model = load_module("chat_model", "models", "chat.model.py")

ChatMessage = chat_model.ChatMessage
ChatSession = chat_model.ChatSession


class ChatRepository:
    def get_or_create_session(
        self,
        session_id: str,
        level: str = "basic",
        topic: str = "python",
    ) -> ChatSession:
        with Session(db.engine) as session:
            chat_session = session.get(ChatSession, session_id)
            if chat_session is None:
                chat_session = ChatSession(id=session_id, level=level, topic=topic)
                session.add(chat_session)
            elif chat_session.level != level or chat_session.topic != topic:
                chat_session.level = level
                chat_session.topic = topic
                session.add(chat_session)
            session.commit()
            session.refresh(chat_session)
            return chat_session

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        user_id: int | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            user_id=user_id,
        )
        with Session(db.engine) as session:
            session.add(message)
            session.commit()
            session.refresh(message)
        return message

    def get_history(self, session_id: str) -> list[ChatMessage]:
        with Session(db.engine) as session:
            statement = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at)
            )
            return list(session.exec(statement).all())

    def clear_history(self, session_id: str) -> None:
        with Session(db.engine) as session:
            statement = delete(ChatMessage).where(
                ChatMessage.session_id == session_id
            )
            session.exec(statement)
            session.commit()


chat_repository = ChatRepository()
