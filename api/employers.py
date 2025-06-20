from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import List
from schemas.response_models import UserSchema
from core.database import get_db
from sqlalchemy.orm import Session
from models.user import Employer as EmployerModel
from auth.utils import require_role, get_current_user  # Added get_current_user
from schemas.user import Employer,EmployerCreate
import logging
router = APIRouter()
logger = logging.getLogger(__name__)

async def get_employers(db: Session) -> List[EmployerModel]:
    try:
        return db.query(EmployerModel).filter(EmployerModel.is_active == True).all()
    except Exception as error:
        print(f'Error getting employers: {error}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch employers"
        )

@router.get("/employers", response_model=List[Employer])
async def get_all_employers(
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),  # Added token authentication
    current_user: UserSchema = Depends(require_role(['admin']))
):
    print("🔍 DEBUG: Fetching all employers")
    employers = await get_employers(db)
    print(f"📦 Found {len(employers)} employers")
    return employers

@router.post("/employers", response_model=Employer)
async def create_employer(
    employer_data: EmployerCreate,
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    try:
        logger.info("🚀 EMPLOYER CREATION START")
        logger.debug(f"📦 Request data: {employer_data.dict()}")

        if not employer_data.name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employer name is required"
            )

        db_employer = EmployerModel(
            name=employer_data.name,
            contact_email=employer_data.contact_email,
            contact_phone=employer_data.contact_phone,
            industry=employer_data.industry,
            is_active=True,
            address=employer_data.address,
            city=employer_data.city,
            state=employer_data.state,
            postcode=employer_data.postcode,
            country=employer_data.country,
            abn=employer_data.abn,
            website=employer_data.website,
            subclients=employer_data.subclients,
            business_units=employer_data.business_units,
            locations=employer_data.locations,
            job_roles=employer_data.job_roles
        )

        db.add(db_employer)
        db.commit()
        db.refresh(db_employer)

        logger.info(f"✅ Employer created with ID: {db_employer.id}")
        return Employer.from_orm(db_employer)  # ✅ Use Pydantic conversion

    except Exception as error:
        logger.error(f"💥 Error creating employer: {error}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employer: {str(error)}"
        )
    
@router.put("/employers/{employer_id}", response_model=Employer)
async def update_employer(
    employer_data: EmployerCreate , 
    employer_id: int = Path(..., gt=0),
    # Reuse the same input model
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    try:
        logger.info(f"🔄 UPDATE: Attempting to update employer with ID: {employer_id}")
        
        db_employer = db.query(EmployerModel).filter(EmployerModel.id == employer_id).first()

        if not db_employer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employer not found"
            )

        for field, value in employer_data.dict(exclude_unset=True).items():
            if hasattr(db_employer, field):
                setattr(db_employer, field, value)

        db.commit()
        db.refresh(db_employer)

        logger.info(f"✅ UPDATE: Successfully updated employer ID {employer_id}")
        return Employer.from_orm(db_employer)

    except Exception as error:
        logger.error(f"❌ UPDATE ERROR: {error}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update employer"
        )
    
@router.delete("/employers/{employer_id}")
async def delete_employer(
    employer_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: UserSchema = Depends(get_current_user),
    current_user: UserSchema = Depends(require_role(['admin']))
):
    try:
        logger.info(f"🗑️ DELETE: Attempting to delete employer with ID: {employer_id}")

        db_employer = db.query(EmployerModel).filter(EmployerModel.id == employer_id).first()

        if not db_employer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employer not found"
            )

        db.delete(db_employer)
        db.commit()

        logger.info(f"✅ DELETE: Successfully deleted employer ID {employer_id}")
        return {"success": True, "message": "Employer deleted successfully"}

    except Exception as error:
        logger.error(f"💥 DELETE ERROR: {error}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employer"
        )
