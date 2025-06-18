# auth/utils.py
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.user import Session as DBSession, User
from schemas.user import User as UserSchema
from core.database import get_db

security = HTTPBearer()
invalidated_tokens = set()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserSchema:
    token = credentials.credentials
    return await validate_token(db, token)

async def validate_token(db: Session, token: str) -> UserSchema:
    try:
        if token in invalidated_tokens:
            print('Token has been invalidated')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        db_session = db.query(DBSession).filter(
            DBSession.token == token,
            DBSession.is_active == True,
            DBSession.expires_at > datetime.utcnow()
        ).first()
        
        if not db_session:
            print(f'No valid session found for token: {token[:10]}...')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        db_session.last_accessed = datetime.utcnow()
        db.commit()
        
        user = db.query(User).filter(User.id == db_session.user_id).first()
        
        if not user or not user.is_active:
            db_session.is_active = False
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User inactive"
            )
        
        return UserSchema.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as error:
        print("Token validation error:", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

async def destroy_token(db: Session, token: str) -> None:
    try:
        db_session = db.query(DBSession).filter(DBSession.token == token).first()
        if db_session:
            db_session.is_active = False
            db.commit()
            
        invalidated_tokens.add(token)
        print(f"Session destroyed and token invalidated: {token[:10]}...")
    except Exception as error:
        print("Token destruction error:", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

def require_role(roles: list[str]):
    def role_checker(current_user: UserSchema = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker