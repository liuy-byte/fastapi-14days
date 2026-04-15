"""Day 8: 项目配置管理"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI 14 Days"
    SECRET_KEY: str = "fastapi-14days-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./fastapi14days.db"

    class Config:
        env_file = ".env"


settings = Settings()
