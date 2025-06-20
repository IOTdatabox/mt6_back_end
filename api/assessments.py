# assessments.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import  Optional
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User, Assessment
from auth.utils import get_current_user, require_role

router = APIRouter()

@router.get("/assessments")
async def get_assessments_with_employee_names(
    consultant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _ = Depends(get_current_user),
    current_user = Depends(require_role(['admin']))
):
    try:
        print("📦 Admin Dashboard - Fetching all assessments")
        
        # Base query for assessments
        query = db.query(Assessment)
        
        # Filter by consultant if provided
        if consultant_id is not None:
            query = query.filter(Assessment.consultant_id == consultant_id)
        
        assessments = query.all()
        results = []
        
        for assessment in assessments:
            user = db.query(User).get(assessment.user_id)
            results.append({
                **assessment.__dict__,
                "employee_name": f"{user.first_name} {user.last_name}" if user else "Unknown Employee"
            })
        
        print(f"📦 Admin assessments fetched: {len(results)}")
        return results
        
    except Exception as error:
        print(f"Error fetching admin assessments: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch assessments"
        )