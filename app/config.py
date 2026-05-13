from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    groq_api_key: str
    app_env: str = "development"
    secret_key: str = "change-me"

    class Config:
        env_file = ".env"


settings = Settings()
