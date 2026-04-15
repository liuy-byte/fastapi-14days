"""Day 7-8: 认证路由"""

from fastapi import APIRouter, Form, HTTPException, status
from sqlmodel import select

from api.deps import CurrentUser, SessionDep
from core.security import create_access_token, get_password_hash, verify_password
from models import Token, User, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(session: SessionDep, user_in: UserCreate):
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    session: SessionDep,
    username: str = Form(description="用户邮箱"),
    password: str = Form(description="密码"),
):
    user = session.exec(select(User).where(User.email == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser):
    return current_user
