from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from auth import verify_password, create_access_token, hash_password
from database import get_db
from pydantic import BaseModel, validator


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

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    team_lead_id = None
    if user.role == "hr" and user.team_lead_id:
        team_lead = db.query(User).filter(User.username == user.team_lead_id).first()
        if not team_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team Lead username not found",
            )
        team_lead_id = team_lead.user_id

    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role,
        team_lead_id=team_lead_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.user_id}



@router.post("/login", tags=["Auth"])
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"user_id": user.user_id})
    return {"access_token": token, "token_type": "bearer"}
