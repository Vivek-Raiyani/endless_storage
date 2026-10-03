from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Template"
    SERVER_HOST: str = "http://localhost:8000"
    DATABASE_URL: str
    FRONTEND_URL: str = "http://localhost:3000"
    # Cookies are sent cross-origin (allow_credentials=True), so origins must be explicit — never "*".
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Drive-like lifecycle settings
    # Items in the trash are permanently purged after this many days (Google Drive uses 30).
    TRASH_RETENTION_DAYS: int = 30
    # Google resumable upload URIs are valid for ~1 week; uploads older than this are abandoned.
    UPLOAD_SESSION_TTL_HOURS: int = 24 * 7

    # Auth Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Set to True in production when serving over HTTPS
    COOKIE_SECURE: bool = False

    # Email Settings
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str = "info@clickcapturr.com"
    RESEND_API_KEY: str | None = None
    
    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None

    # Google Drive Storage Settings
    # Scope for Drive access (full access needed for sharing/copying files during account migration)
    GOOGLE_DRIVE_SCOPE: str = "https://www.googleapis.com/auth/drive"
    # Fixed chunk size for all file splits (default: 256 MB)
    CHUNK_SIZE_BYTES: int = 256 * 1024 * 1024
    # Fernet symmetric key (base64-url-encoded 32 bytes) for encrypting Drive refresh tokens at rest
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    TOKEN_ENCRYPTION_KEY: str | None = None


    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
