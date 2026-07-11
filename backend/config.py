from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    max_file_mb: int = 100
    secret_key: str = "changeme"
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"


settings = Settings()
