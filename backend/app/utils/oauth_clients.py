from authlib.integrations.starlette_client import OAuth
from app.core.config import settings

oauth = OAuth()

# Google OAuth for Authentication (Login/Signup)
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID or "placeholder",
    client_secret=settings.GOOGLE_CLIENT_SECRET or "placeholder",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Google OAuth for Google Drive Storage Integration
oauth.register(
    name="google_drive",
    client_id=settings.GOOGLE_CLIENT_ID or "placeholder",
    client_secret=settings.GOOGLE_CLIENT_SECRET or "placeholder",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": f"openid email {settings.GOOGLE_DRIVE_SCOPE}",
        "access_type": "offline",
        "prompt": "consent",  # Forces Google to always return a refresh_token
    },
)
