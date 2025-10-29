from typing import Optional, List, Union

from pydantic import PostgresDsn, computed_field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    VERSION: str = "0.1"
    ALLOW_ORIGINS: Union[str, List[str]] = "*"
    DEBUG: bool = False
    SQLALCHEMY_DEBUG: bool = False
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    PAGE_DEFAULT: Optional[int] = 1
    LIMIT_DEFAULT: Optional[int] = 10
    ACCESS_TOKEN_EXPIRES_IN_MINUTES: int = 1
    REFRESH_TOKEN_EXPIRES_IN_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    UPLOAD_PATH: str = "uploads"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_PUBLIC_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str
    MINIO_SECURE: bool = False
    MINIO_PUBLIC_SECURE: bool = False

    @field_validator("ALLOW_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @computed_field
    @property
    def database_url(self) -> str:
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            path=f"{self.POSTGRES_DB}",
        ))


settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
