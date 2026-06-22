from sqlmodel import Session, select

from helper.import_helper import load_module

db = load_module("database", "config", "database.py")
chat_model = load_module("chat_model", "models", "chat.model.py")

User = chat_model.User


class UserRepository:
    def create(self, username: str, email: str, password: str) -> User:
        user = User(username=username, email=email, password=password)
        with Session(db.engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def get_by_username(self, username: str) -> User | None:
        with Session(db.engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()

    def get_by_email(self, email: str) -> User | None:
        with Session(db.engine) as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()

    def get_by_id(self, user_id: int) -> User | None:
        with Session(db.engine) as session:
            return session.get(User, user_id)


user_repository = UserRepository()
