from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from models.user import User
from schemas.user import User as UserSchema
from auth.utils import get_current_user
router = APIRouter()

@router.get("/employees", response_model=List[UserSchema])
async def get_consultant_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user has consultant role
    if current_user.role != "consultant":
        raise HTTPException(
            status_code=403, 
            detail="Only consultants can access this endpoint"
        )
    
    print(f"📦 Consultant Dashboard - Fetching scoped employees for consultant: {current_user.id}")
    
    try:
        # Get employees assigned to this consultant using created_by_consultant_id
        employees = db.query(User).filter(
            User.created_by_consultant_id != current_user.id,
            User.is_active == True
        ).all()
        
        print(f"📦 Scoped employees for consultant: {len(employees)}")
        
        return employees
        
    except Exception as e:
        print(f"Error fetching consultant employees: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch employees"
        )