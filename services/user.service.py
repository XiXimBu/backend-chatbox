import hashlib
import secrets

from helper.import_helper import load_module

user_repo = load_module("user_repository", "repositories", "user.respository.py")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    )
    return f"{salt}${hashed.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$", 1)
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    )
    return secrets.compare_digest(hashed, check.hex())


class UserService:
    def register(self, username: str, email: str, password: str):
        if user_repo.user_repository.get_by_username(username):
            raise ValueError("Tên đăng nhập đã tồn tại")

        if user_repo.user_repository.get_by_email(email):
            raise ValueError("Email đã được sử dụng")

        hashed = hash_password(password)
        return user_repo.user_repository.create(username, email, hashed)

    def login(self, username: str, password: str):
        user = user_repo.user_repository.get_by_username(username)
        if user is None:
            user = user_repo.user_repository.get_by_email(username)

        if user is None or not verify_password(password, user.password):
            raise ValueError("Tên đăng nhập hoặc mật khẩu không đúng")

        return user


user_service = UserService()
