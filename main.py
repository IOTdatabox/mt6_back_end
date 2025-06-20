from fastapi import  FastAPI
from api import users
from api import employers
from api import consultants
from api import employees
from api import assessments
from api.consultant import employees
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router, prefix="/api/auth", tags=["users"])
app.include_router(employers.router,prefix="/api/admin",tags=["admin"])
app.include_router(consultants.router,prefix="/api/admin",tags=["admin"])
app.include_router(employees.router,prefix="/api/admin",tags=["admin"])
app.include_router(assessments.router,prefix="/api/admin",tags=["admin"])
app.include_router(employees.router,prefix="/api/consultant",tags=["consultant"])