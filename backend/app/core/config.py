from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Template"
    SERVER_HOST: str = "http://localhost:8000"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    STORAGE_PROVIDER: str = "local"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # AWS S3 Settings
    AWS_ENDPOINT: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION_NAME: str | None = None
    AWS_BUCKET_NAME: str | None = None
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None


    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
