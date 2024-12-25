from fastapi import FastAPI, Depends
from src.database import engine, Base
from src.routers.users import router
from src.routers.resumes import router_res
from src.routers.vacancies import router_vac
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.database import Base, engine
from datetime import datetime
from src.database import get_db, SessionLocal as session_local
from src.models import User, RoleEnum as UserRoleEnum

app = FastAPI(title="HR Monitor", debug=False)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
app.include_router(router, prefix="/api/v1", tags=["Users"])
app.include_router(router_vac, prefix="/api/v2")
app.include_router(router_res, prefix="/api/v3")


def create_supervisor(db: Session = Depends(get_db)):
    admin_exists = db.query(User).filter(User.role == UserRoleEnum.team_lead_hr).first()
    if not admin_exists:
        hashed_password = CryptContext(schemes=["bcrypt"]).hash("admin")
        new_admin = User(
            username="admin",
            password_hash=hashed_password,
            is_active=True,
            role=UserRoleEnum.team_lead_hr,
            created_at=datetime.utcnow(),
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Admin user created!")


@app.on_event("startup")
def on_startup():
    db = session_local()
    try:
        create_supervisor(db)
    finally:
        db.close()
