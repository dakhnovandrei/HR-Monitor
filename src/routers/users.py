from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from src.models import User
from src.routers.auth import (
    create_access_token,
    hash_password,
    pwd_context,
    create_refresh_token,
)
from src.database import get_db
from pydantic import BaseModel, validator

import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    team_lead_username: Optional[str] = None

    @validator("role")
    def validate_role(cls, role):
        valid_roles = ["hr", "team_lead_hr"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of {valid_roles}")
        return role


router = APIRouter()


@router.post("/register", tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    print(user.dict())
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # team_lead_id = None
    # if user.role == "hr":
    #     if not user.team_lead_username:
    #         raise HTTPException(status_code=400, detail="Team lead username is required for HR role")
    #     team_lead = db.query(User).filter(User.username == user.team_lead_username).first()
    #     if not team_lead:
    #         raise HTTPException(status_code=404, detail="Team lead username not found")
    #     team_lead_id = team_lead.user_id

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role,
        team_lead_id=1,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.user_id}


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str


@router.post("/login", summary="Login in account")
async def login(
    login: str,
    password: str,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = db.query(User).filter(User.username == login).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Некорректный email или пароль")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        key="refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        samesite="lax",
    )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)
