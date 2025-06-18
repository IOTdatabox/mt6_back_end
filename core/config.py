from pydantic_settings import BaseSettings  # ✅ use pydantic_settings instead of pydantic

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
