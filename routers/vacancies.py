from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Vacancies, User, Resumes
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import require_role

router_vac = APIRouter()


class VacancyCreate(BaseModel):
    title: str
    description: Optional[str]
    status: str


class VacancyResponse(BaseModel):
    vacancy_id: int
    title: str
    description: Optional[str]
    status: str
    created_by: int


class StatisticsResponse(BaseModel):
    username: str
    current_stage: str
    resume_count: int


@router_vac.post("/create-vacancy", tags=["Vacancies"])
def create_vacancy(
        vacancy: VacancyCreate,
        current_user: User = Depends(require_role(["team_lead_hr"])),
        db: Session = Depends(get_db)
):
    new_vacancy = Vacancies(
        title=vacancy.title,
        description=vacancy.description,
        created_by=current_user.user_id,
        status=vacancy.status,
    )
    db.add(new_vacancy)
    db.commit()
    db.refresh(new_vacancy)
    return {"message": "Vacancy created successfully", "vacancy_id": new_vacancy.vacancy_id}


@router_vac.get("/statistics", tags=["Statistics"])
def get_statistics(
        current_user: User = Depends(require_role(["team_lead_hr"])),
        db: Session = Depends(get_db)
):
    hr_statistics = (
        db.query(User.username, Resumes.current_stage, db.func.count(Resumes.resume_id))
        .join(Resumes, User.user_id == Resumes.hr_id)
        .filter(User.team_lead_id == current_user.user_id)
        .group_by(User.username, Resumes.current_stage)
        .all()
    )
    return {"statistics": hr_statistics}
