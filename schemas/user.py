from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Shared schemas
class PoseKeypoint(BaseModel):
    x: float
    y: float
    visibility: float

class PoseData(BaseModel):
    landmarks: List[PoseKeypoint]
    timestamp: float
    session_id: Optional[str] = None

class MovementMetrics(BaseModel):
    exercise_type: str
    duration: float
    frame_count: int
    frame_rate: float
    joint_angles: Dict[str, Any]
    range_of_motion: Dict[str, Any]
    movement_velocity: Dict[str, Any]
    stability_metrics: Dict[str, float]
    clinical_notes: List[str]

class MovementScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    joint_scores: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)
    movement_metrics: Optional[MovementMetrics] = None
    exercise_index: Optional[int] = None
    exercise_name: Optional[str] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None

# Request/Response schemas
class UserBase(BaseModel):
    email: str
    role: str = "consultant"  # default value
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")

    class Config:
        populate_by_name = True

class UserCreate(UserBase):
    password: Optional[str] = None
    username: Optional[str] = None
    dob_year: Optional[int] = None
    employee_id: Optional[str] = None
    subclient: Optional[str] = None
    business_unit: Optional[str] = None
    location: Optional[str] = None
    job_role: Optional[str] = None
    created_by_consultant_id: Optional[int] = None
    assigned_locations: Optional[List[str]] = Field(None, alias="assignedLocations")
    business_unit: Optional[str] = Field(None, alias="businessUnit")
    invited: bool = False
    employer_id: Optional[int] = Field(None, alias="employerId")
    jobRoleId: Optional[int] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    qualifications: Optional[str] = None
    license_number: Optional[str] = Field(None, alias="licenseNumber")
    city: Optional[str] = None
    state: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class EmployerBase(BaseModel):
    name: str = Field(..., alias="employerName")
    industry: Optional[str] = None
    contact_email: Optional[str] = Field(None, alias="contactEmail")
    contact_phone: Optional[str] = Field(None, alias="contactPhone")

    model_config = {
        "populate_by_name": True,
    }

class EmployerCreate(EmployerBase):
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: str = "Australia"
    abn: Optional[str] = None
    website: Optional[str] = None
    is_active: bool = True 
    subclients: List[str] = Field(default_factory=list)
    business_units: List[str] = Field(default_factory=list, alias="businessUnits")
    locations: List[str] = Field(default_factory=list)
    job_roles: List[str] = Field(default_factory=list, alias="jobRoles")

    model_config = {
        "populate_by_name": True,
    }

class Employer(EmployerBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }

class AssessmentBase(BaseModel):
    assessment_id: str
    user_id: int
    assessment_type: str
    title: str

class AssessmentCreate(AssessmentBase):
    consultant_id: Optional[int] = None
    description: Optional[str] = None
    status: str = "scheduled"
    overall_progress: float = 0
    scheduled_date: Optional[datetime] = None

class Assessment(AssessmentBase):
    id: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssessmentSessionBase(BaseModel):
    session_id: str
    assessment_type: str

class AssessmentSessionCreate(AssessmentSessionBase):
    user_id: Optional[int] = None
    consultant_id: Optional[int] = None
    assessment_id: Optional[str] = None
    session_number: int = 1
    session_type: str = "initial"
    completed_at: Optional[datetime] = None

class AssessmentSession(AssessmentSessionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    category: str
    difficulty: str

class ExerciseCreate(ExerciseBase):
    description: Optional[str] = None
    target_joints: Optional[List[str]] = None
    duration: Optional[int] = None

class Exercise(ExerciseBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True