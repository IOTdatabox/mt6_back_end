
from datetime import datetime, timedelta
from typing import Optional
from api.users import LoginResponse
import bcrypt
from sqlalchemy.orm import Session
import secrets
from models.user import User, Session as DBSession
from schemas.user import User as UserSchema
async def authenticate_user(db: Session, username: str, password: str) -> Optional[LoginResponse]:
    try:
        print("Attempting authentication for:", username)
        
        # Direct database query
        user = db.query(User).filter(User.username == username).first()
        
        print("Database query result:", {
            "id": user.id if user else None,
            "username": user.username if user else None,
            "role": user.role if user else None,
            "hasPassword": bool(user.password) if user else False,
            "isActive": user.is_active if user else False
        } if user else "No user found")
        
        if not user:
            print("User not found")
            return None
        
        # Check password using bcrypt for hashed passwords or direct comparison for plain text (admin)
        print("Password verification debug:")
        print(f"  - User password starts with $2b$: {user.password.startswith('$2b$')}")
        print(f"  - Input password: {password}")
        print(f"  - Stored password hash: {user.password[:20]}...")
        
        is_password_valid = (
            bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')) 
            if user.password.startswith('$2b$') 
            else user.password == password
        )
        
        print(f"  - Password validation result: {is_password_valid}")
        
        if not is_password_valid:
            print("Password mismatch")
            return None
        
        if not user.is_active:
            print("User inactive")
            return None
        
        # Create session in database
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)  # 24 hours
        
        db_session = DBSession(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(db_session)
        db.commit()
        
        print("Authentication successful, database session created")
        
        # Return user without password
        user_data = UserSchema.from_orm(user)
        return LoginResponse(
            user=user_data,
            token=token
        )
        
    except Exception as error:
        print("Authentication error:", error)
        return None