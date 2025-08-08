from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = True

    # Database and services (placeholders for now)
    database_url: str = "postgresql://postgres:postgres@localhost:5432/bank_app"
    redis_url: str = "redis://localhost:6379/0"
    object_store_endpoint: str = "http://localhost:9000"
    object_store_bucket: str = "documents"
    object_store_access_key: str = "minioadmin"
    object_store_secret_key: str = "minioadmin"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()