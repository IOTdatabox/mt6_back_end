from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.response_models import UserSchema
from core.database import get_db
from sqlalchemy.orm import Session
from models.user import User as UserModel
from auth.utils import require_role, get_current_user
from schemas.user import User

router = APIRouter()

async def get_users_by_role(db: Session, role: str) -> List[UserModel]:
    try:
        return db.query(UserModel).filter(
            UserModel.role == role,
            UserModel.is_active == True
        ).all()
    except Exception as error:
        print(f'Error getting users by role {role}: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )

@router.get("/employees", response_model=List[User])
async def get_all_employees(
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    print("📦 Admin Dashboard - Fetching all employees")
    employees = await get_users_by_role(db, 'employee')
    print(f"📦 Admin employees fetched: {len(employees)}")
    return employees