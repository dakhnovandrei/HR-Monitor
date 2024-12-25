from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.models import Resumes, User, Vacancies, StageEnum
from src.database import get_db
from src.routers.auth import require_role
from pydantic import BaseModel
from typing import Optional
from datetime import date
import datetime
from sqlalchemy.sql import func

class UpdateStageRequest(BaseModel):
    resume_id: int
    new_stage: StageEnum

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
    db: Session = Depends(get_db),
):
    vacancy = (
        db.query(Vacancies).filter(Vacancies.vacancy_id == resume.vacancy_id).first()
    )
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
    return {
        "message": "Resume uploaded successfully",
        "resume_id": new_resume.resume_id,
    }


@router_res.get("/resumes", tags=["Resumes"])
def get_resumes(
    filters: FilterParams = Depends(),
    current_user: User = Depends(require_role(["hr"])),
    db: Session = Depends(get_db),
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

@router_res.get("/statistics/hr", tags=["Statistics"])
def hr_statistics(
    current_user = Depends(require_role(["hr"])),
    db: Session = Depends(get_db),
):
   
    avg_stage_time = (
        db.query(
            Resumes.current_stage,
            func.avg(
                func.extract(
                    'epoch', func.age(Resumes.status_change_date, Resumes.upload_date)
                ) / 86400.0  
            ).label("avg_time"),
        )
        .filter(Resumes.hr_id == current_user.user_id)
        .group_by(Resumes.current_stage)
        .all()
    )

    resume_stage_distribution = (
        db.query(
            Resumes.current_stage,
            func.count(Resumes.resume_id).label("count"),
        )
        .filter(Resumes.hr_id == current_user.user_id)
        .group_by(Resumes.current_stage)
        .all()
    )


    resume_source_distribution = (
        db.query(
            Resumes.source,
            func.count(Resumes.resume_id).label("count"),
        )
        .filter(Resumes.hr_id == current_user.user_id)
        .group_by(Resumes.source)
        .all()
    )

   
    avg_candidates_per_vacancy = (
        db.query(
            func.avg(
                db.query(func.count(Resumes.resume_id))
                .filter(Resumes.vacancy_id == Vacancies.vacancy_id)
                .correlate(Vacancies)
                .as_scalar()
            ).label("avg_candidates")
        )
        .filter(Vacancies.created_by == current_user.user_id)
        .scalar()
    )

    return {
        "avg_stage_time": [
            {"stage": row[0], "avg_time_days": round(row[1], 2) if row[1] else 0}
            for row in avg_stage_time
        ],
        "resume_stage_distribution": [
            {"stage": row[0], "count": row[1]} for row in resume_stage_distribution
        ],
        "resume_source_distribution": [
            {"source": row[0] or "Unknown", "count": row[1]} for row in resume_source_distribution
        ],
        "avg_candidates_per_vacancy": round(avg_candidates_per_vacancy, 2)
        if avg_candidates_per_vacancy
        else 0,
    }
@router_res.put("/resumes/update-stage", tags=["Resumes"])
def update_resume_stage(
    update_request: UpdateStageRequest,
    current_user = Depends(require_role(["hr"])),
    db: Session = Depends(get_db),
):

    resume = db.query(Resumes).filter(Resumes.resume_id == update_request.resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if current_user.role == "hr" and resume.hr_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    
    resume.current_stage = update_request.new_stage
    resume.status_change_date = datetime.datetime.utcnow()

    db.commit()
    db.refresh(resume)

    return {
        "message": "Resume stage updated successfully",
        "resume_id": resume.resume_id,
        "new_stage": resume.current_stage,
        "status_change_date": resume.status_change_date,
    }
