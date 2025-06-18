# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from core.database import get_db
from auth.utils import get_current_user, destroy_token
from schemas.response_models import (
    LoginRequest,
    LoginResponse,
    ValidateSessionResponse,
    UserMeResponse,
    LogoutResponse,
    UserSchema
)
from auth.user import authenticate_user
from typing import Optional

router = APIRouter()

@router.post("/login", response_model=LoginResponse, tags=["auth"])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        if not login_data.username or not login_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password required"
            )

        auth_result = await authenticate_user(db, login_data.username, login_data.password)
        
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        return auth_result
    except Exception as e:
        print("Login error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/validate-session", 
            response_model=ValidateSessionResponse,
            tags=["auth"])
async def validate_session(
    current_user: UserSchema = Depends(get_current_user)
):
    try:
        return {"valid": True, "user": current_user}
    except Exception as error:
        print("Session validation error:", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session validation failed"
        )

@router.get("/me", response_model=UserMeResponse, tags=["auth"])
async def get_me(
    current_user: UserSchema = Depends(get_current_user)
):
    try:
        return {"user": current_user}
    except Exception as error:
        print("Auth me error:", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

@router.post("/logout", response_model=LogoutResponse, tags=["auth"])
async def logout(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        
        token = authorization.replace('Bearer ', '')
        await destroy_token(db, token)
        return {"message": "Logged out successfully"}
    except HTTPException:
        raise
    except Exception as error:
        print("Logout error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/logout", response_model=LogoutResponse, tags=["auth"])
async def legacy_logout(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    try:
        if not authorization:
            return {"message": "Logged out successfully"}
        
        token = authorization.replace('Bearer ', '')
        if token:
            await destroy_token(db, token)
        return {"message": "Logged out successfully"}
    except HTTPException:
        raise
    except Exception as error:
        print("Logout error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )