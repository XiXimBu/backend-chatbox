from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from helper.import_helper import load_module

user_service_mod = load_module("user_service", "services", "user.service.py")

router = APIRouter(prefix="/api", tags=["user"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest):
    try:
        user = user_service_mod.user_service.register(
            request.username,
            request.email,
            request.password,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return UserResponse(id=user.id, username=user.username, email=user.email)


@router.post("/login", response_model=UserResponse)
def login(request: LoginRequest):
    try:
        user = user_service_mod.user_service.login(
            request.username,
            request.password,
        )
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))

    return UserResponse(id=user.id, username=user.username, email=user.email)
