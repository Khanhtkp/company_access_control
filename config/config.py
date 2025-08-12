from pydantic import BaseSettings

class Settings(BaseSettings):
    email_user: str
    email_pass: str
    llm_api_key: str

    class Config:
        env_file = "config/.env"
        env_file_encoding = "utf-8"

settings = Settings()