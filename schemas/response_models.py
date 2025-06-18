# schemas/response_models.py
from pydantic import BaseModel
from schemas.user import User as UserSchema

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user: UserSchema
    token: str

class ValidateSessionResponse(BaseModel):
    valid: bool
    user: UserSchema

class UserMeResponse(BaseModel):
    user: UserSchema

class LogoutResponse(BaseModel):
    message: str