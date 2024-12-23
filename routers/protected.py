from fastapi import APIRouter, Depends
from auth import require_role
from models import User

router_prot = APIRouter()

@router_prot.get("/hr-only", tags=["Protected Routes"])
def hr_only_route(current_user: User = Depends(require_role(["hr"]))):
    return {"message": f"Hello HR: {current_user.username}"}

@router_prot.get("/team-lead-only", tags=["Protected Routes"])
def team_lead_only_route(current_user: User = Depends(require_role(["team_lead_hr"]))):
    return {"message": f"Hello Team Lead HR: {current_user.username}"}

@router_prot.get("/all-roles", tags=["Protected Routes"])
def all_roles_route(current_user: User = Depends(require_role(["hr", "team_lead_hr"]))):
    return {"message": f"Hello {current_user.role}: {current_user.username}"}
