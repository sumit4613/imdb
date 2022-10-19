from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "IMDB"
    API_V1_STR: str = "/api/v1"
    ALGORITHM: str = "HS256"
    ADMIN_EMAIL: str = "root@example.com"
    ADMIN_PASSWORD: str = "test@123"
    ADMIN_NAME: str = "Admin"
    SECRET_KEY: str = "y69_IxPxaqH5fY1aXEaFCsuOQikzK_XnIzSbJ0cnBok"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Database
    # update this to your database url
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = "postgresql://db_user:db_passwd@db:5432/imdb"
    SQLALCHEMY_TEST_DATABASE_URI: Optional[PostgresDsn] = "postgresql://db_user:db_passwd@db:5432/tests"

    class Config:
        case_sensitive = True


settings = Settings()
