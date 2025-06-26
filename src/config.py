from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TOKEN: str
    ADMIN_CHAT_ID: int

    DB_DSN: str = "postgresql://user:pass@localhost:5432/db"

    class Config:
        env_file = '.env'


config = Settings()
