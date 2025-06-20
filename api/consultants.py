import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from schemas.user import  UserCreate, User
from schemas.response_models import UserSchema
from core.database import get_db
from models.user import User as UserModel
from models.user import Employer  # Make sure you have this imported for employer lookup
from auth.utils import require_role, get_current_user
import logging

router = APIRouter()

# Your existing GET request - unchanged
async def get_consultants_with_details(db: Session) -> List[UserModel]:
    try:
        return db.query(UserModel).filter(
            UserModel.is_active == True,
            UserModel.role == 'consultant'
        ).all()
    except Exception as error:
        logging.error(f'Error getting consultants: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch consultants"
        )

@router.get("/consultants", response_model=List[UserSchema])
async def get_all_consultants(
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    logging.info("🔍 DEBUG: Fetching all consultants")
    consultants = await get_consultants_with_details(db)
    logging.info(f"📦 Found {len(consultants)} consultants")
    return consultants

# /api/admin/consultants
# New POST request converted from your Express code
@router.post("/consultants", response_model=User)
async def create_consultant(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['admin']))
):
    
    if not user_in.email or not user_in.first_name or not user_in.last_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, first_name, and last_name are required"
        )

    # Validate employer and assigned locations
    if user_in.employer_id and user_in.assigned_locations:
        employer = db.query(Employer).filter(Employer.id == user_in.employer_id).first()
        if not employer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected employer not found"
            )
        invalid_locations = [
            loc for loc in user_in.assigned_locations
            if not employer.locations or loc not in employer.locations
        ]
        if invalid_locations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid locations for selected employer: {', '.join(invalid_locations)}"
            )

    consultant_data = {
        "email": user_in.email,
        "first_name": user_in.first_name,
        "last_name": user_in.last_name,
        "phone": user_in.phone,
        "role": user_in.role or "consultant",
        "specialization": user_in.specialization,
        "qualifications": user_in.qualifications,
        "license_number": user_in.license_number,
        "city": user_in.city,
        "state": user_in.state,
        "employer_id": user_in.employer_id,
        "assigned_locations": user_in.assigned_locations or [],
        "is_active": True  # default active, adjust if you want to handle input
    }

    try:
        # Check existing email
        existing_user = db.query(UserModel).filter(UserModel.email == user_in.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists. Please use a different email address."
            )

        new_consultant = UserModel(**consultant_data)
        db.add(new_consultant)
        db.commit()
        db.refresh(new_consultant)

        logging.info(f"✅ SUCCESS: Consultant created with ID: {new_consultant.id}")

        return new_consultant

    except HTTPException:
        raise
    except Exception as error:
        logging.error(f"💥 CONSULTANT CREATION ERROR: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create consultant"
        )

@router.put("/consultants/{consultant_id}", response_model=UserSchema)
async def update_consultant(
    consultant_id: int = Path(..., description="ID of the consultant to update"),
    update_data: Dict[str, Any] = None,  # or use a Pydantic model UserUpdate
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    logging.info(f"🔍 DEBUG: Updating consultant ID: {consultant_id}")
    logging.info(f"🔍 DEBUG: Update data: {update_data}")

    existing_consultant = db.query(UserModel).filter(UserModel.id == consultant_id).first()
    if not existing_consultant:
        logging.error(f"❌ Consultant not found with ID: {consultant_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")

    # Validate assigned locations against employer's available locations
    employer_id = update_data.get("employer_id")
    assigned_locations = update_data.get("assigned_locations", [])
    if employer_id and assigned_locations:
        employer = db.query(Employer).filter(Employer.id == employer_id).first()
        if not employer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected employer not found")

        invalid_locations = [loc for loc in assigned_locations if not employer.locations or loc not in employer.locations]
        if invalid_locations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid locations for selected employer: {', '.join(invalid_locations)}"
            )

    # Handle password update
    password = update_data.get("password")
    if password == '':
        logging.info("🔒 Removing empty password from update")
        update_data.pop("password")
    elif password:
        logging.info("🔒 Hashing new password")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        update_data["password"] = hashed.decode('utf-8')

    # Update the consultant fields dynamically
    for field, value in update_data.items():
        if hasattr(existing_consultant, field):
            setattr(existing_consultant, field, value)

    try:
        db.commit()
        db.refresh(existing_consultant)
        logging.info(f"✅ Updated consultant with ID: {consultant_id}")
        return existing_consultant
    except Exception as error:
        logging.error(f"❌ Error updating consultant: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update consultant"
        )

# DELETE /consultants/{id} - Delete consultant
@router.delete("/consultants/{consultant_id}")
async def delete_consultant(
    consultant_id: int = Path(..., description="ID of the consultant to delete"),
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    logging.info(f"🔍 DEBUG: Deleting consultant ID: {consultant_id}")

    existing_consultant = db.query(UserModel).filter(UserModel.id == consultant_id).first()
    if not existing_consultant:
        logging.error(f"❌ Consultant not found with ID: {consultant_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultant not found")

    try:
        db.delete(existing_consultant)
        db.commit()
        logging.info(f"✅ Deleted consultant with ID: {consultant_id}")
        return {"message": "Consultant deleted successfully"}
    except Exception as error:
        logging.error(f"❌ Error deleting consultant: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete consultant"
        )