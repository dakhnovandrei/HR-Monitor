# models.py
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base
import enum
import datetime


class RoleEnum(str, enum.Enum):
    hr = "hr"
    team_lead_hr = "team_lead_hr"


class VacancyStatusEnum(str, enum.Enum):
    open = "open"
    closed = "closed"


class StageEnum(str, enum.Enum):
    opened = "opened"
    reviewed = "reviewed"
    hr_interview = "hr_interview"
    hr_interview_passed = "hr_interview_passed"
    tech_interview = "tech_interview"
    tech_interview_passed = "tech_interview_passed"
    offer = "offer"


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("hr", "team_lead_hr", name="role_enum"), nullable=False)
    team_lead_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.datetime.utcnow())
    team_lead = relationship("User", remote_side=[user_id])


class Vacancies(Base):
    __tablename__ = "vacancies"
    vacancy_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_date = Column(Date, default=datetime.datetime.utcnow())
    status = Column(Enum(VacancyStatusEnum), default=VacancyStatusEnum.open)


class Resumes(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vacancy_id = Column(Integer, ForeignKey("vacancies.vacancy_id"), nullable=False)
    hr_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    source = Column(String(100))
    upload_date = Column(Date, default=datetime.datetime.utcnow())
    current_stage = Column(Enum(StageEnum), default="opened")
    sla_deadline = Column(Date)
    status_change_date = Column(Date, nullable=True)


class Stages(Base):
    __tablename__ = "stages"
    stage_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.resume_id"), nullable=False)
    stage = Column(Enum(StageEnum), nullable=False)
    start_date = Column(Date, default="CURRENT_DATE")
    end_date = Column(Date)


class SLA_Settings(Base):
    __tablename__ = "sla_settings"
    sla_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stage = Column(Enum(StageEnum), nullable=False)
    max_days = Column(Integer, nullable=False)
