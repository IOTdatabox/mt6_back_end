from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime, JSON, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Enums for various fields
class RoleEnum(str, Enum):
    admin = "admin"
    employer = "employer"
    consultant = "consultant"
    employee = "employee"

class AssessmentTypeEnum(str, Enum):
    pre_employment = "pre_employment"
    return_to_work = "return_to_work"
    periodic = "periodic"
    injury_assessment = "injury_assessment"
    manual = "manual"
    camera = "camera"
    validation = "validation"

class AssessmentStatusEnum(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class SessionTypeEnum(str, Enum):
    initial = "initial"
    follow_up = "follow_up"
    final = "final"
    additional = "additional"

class OutcomeEnum(str, Enum):
    cleared = "cleared"
    restricted = "restricted"
    requires_treatment = "requires_treatment"
    pending_review = "pending_review"

class EscalationLevelEnum(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class DifficultyEnum(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

# Models/Tables
class JobRole(Base):
    __tablename__ = "job_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="sessions")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(RoleEnum), nullable=False, default=RoleEnum.consultant)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    
    # Employee-specific fields
    dob_year = Column(Integer)
    employee_id = Column(String, unique=True)
    subclient = Column(String)
    business_unit = Column(String)
    location = Column(String)
    job_role = Column(String)
    created_by_consultant_id = Column(Integer, ForeignKey("users.id"))
    
    # Consultant-specific fields
    assigned_locations = Column(JSON, default=[])
    invited = Column(Boolean, default=False)
    invited_at = Column(DateTime)
    has_logged_in = Column(Boolean, default=False)
    
    # Common organizational reference
    employer_id = Column(Integer, ForeignKey("employers.id"))
    
    # Additional fields
    phone = Column(String)
    specialization = Column(String)
    qualifications = Column(String)
    license_number = Column(String)
    city = Column(String)
    state = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships - ONLY THESE LINES ARE CHANGED
    sessions = relationship("Session", back_populates="user")
    employer = relationship("Employer", back_populates="users")
    created_employees = relationship("User", remote_side=[id])
    assessments = relationship(
        "Assessment", 
        back_populates="user",
        foreign_keys="Assessment.user_id"
    )
    consultant_assessments = relationship(
        "Assessment", 
        back_populates="consultant",
        foreign_keys="Assessment.consultant_id"
    )

class Employer(Base):
    __tablename__ = "employers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    postcode = Column(String)
    country = Column(String, default="Australia")
    abn = Column(String)
    website = Column(String)
    
    # Array fields
    subclients = Column(JSON, default=[])
    business_units = Column(JSON, default=[])
    locations = Column(JSON, default=[])
    job_roles = Column(JSON, default=[])
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="employer")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consultant_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(SQLAlchemyEnum(AssessmentTypeEnum), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(SQLAlchemyEnum(AssessmentStatusEnum), default=AssessmentStatusEnum.scheduled)
    overall_progress = Column(Float, default=0)
    final_score = Column(Float)
    final_recommendations = Column(JSON)
    scheduled_date = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships - ONLY THESE LINES ARE CHANGED
    user = relationship(
        "User", 
        back_populates="assessments",
        foreign_keys=[user_id]
    )
    consultant = relationship(
        "User", 
        back_populates="consultant_assessments",
        foreign_keys=[consultant_id]
    )
    sessions = relationship("AssessmentSession", back_populates="assessment")

class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    consultant_id = Column(Integer, ForeignKey("users.id"))
    assessment_type = Column(SQLAlchemyEnum(AssessmentTypeEnum), nullable=False)
    assessment_id = Column(String, ForeignKey("assessments.assessment_id"))
    session_number = Column(Integer, default=1)
    session_type = Column(SQLAlchemyEnum(SessionTypeEnum), default=SessionTypeEnum.initial)
    overall_score = Column(Float)
    joint_scores = Column(JSON)
    movement_data = Column(JSON)
    movement_metrics = Column(JSON)
    recommendations = Column(JSON)
    consultant_notes = Column(Text)
    outcome = Column(SQLAlchemyEnum(OutcomeEnum))
    escalation_level = Column(SQLAlchemyEnum(EscalationLevelEnum), default=EscalationLevelEnum.none)
    assigned_exercises = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="sessions")
    user = relationship("User", foreign_keys=[user_id])
    consultant = relationship("User", foreign_keys=[consultant_id])

class Exercise(Base):
    __tablename__ = "exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String, nullable=False)
    target_joints = Column(JSON)
    difficulty = Column(SQLAlchemyEnum(DifficultyEnum), nullable=False)
    duration = Column(Integer)
    is_active = Column(Boolean, default=True)