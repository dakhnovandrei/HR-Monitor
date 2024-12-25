from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Resumes, User, Vacancies
from database import get_db
from routers.auth import require_role
from pydantic import BaseModel
from typing import Optional
from datetime import date


class ResumeCreate(BaseModel):
    vacancy_id: int
    source: Optional[str]
    sla_deadline: date


class ResumeResponse(BaseModel):
    resume_id: int
    vacancy_id: int
    hr_id: int
    source: Optional[str]
    upload_date: date
    current_stage: str
    sla_deadline: date


class FilterParams(BaseModel):
    vacancy_id: Optional[int]
    stage: Optional[str]
    date_from: Optional[date]
    date_to: Optional[date]


router_res = APIRouter()


@router_res.post("/upload-resume", tags=["Resumes"])
def upload_resume(
        resume: ResumeCreate,
        current_user: User = Depends(require_role(["hr"])),
        db: Session = Depends(get_db)
):
    vacancy = db.query(Vacancies).filter(Vacancies.vacancy_id == resume.vacancy_id).first()
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacancy not found")

    new_resume = Resumes(
        vacancy_id=resume.vacancy_id,
        hr_id=current_user.user_id,
        source=resume.source,
        sla_deadline=resume.sla_deadline,
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    return {"message": "Resume uploaded successfully", "resume_id": new_resume.resume_id}


@router_res.get("/resumes", tags=["Resumes"])
def get_resumes(
        filters: FilterParams = Depends(),
        current_user: User = Depends(require_role(["hr"])),
        db: Session = Depends(get_db)
):
    query = db.query(Resumes).filter(Resumes.hr_id == current_user.user_id)

    if filters.vacancy_id:
        query = query.filter(Resumes.vacancy_id == filters.vacancy_id)
    if filters.stage:
        query = query.filter(Resumes.current_stage == filters.stage)
    if filters.date_from:
        query = query.filter(Resumes.upload_date >= filters.date_from)
    if filters.date_to:
        query = query.filter(Resumes.upload_date <= filters.date_to)

    resumes = query.all()
    return resumes
