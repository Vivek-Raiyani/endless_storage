import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import api_router
from app.core.config import settings

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Format name: app.utils.emails -> utils/emails
        name_parts = record.name.split('.')
        if name_parts[0] == 'app' and len(name_parts) > 1:
            mod_name = '/'.join(name_parts[1:])
        else:
            mod_name = record.name
            
        record.custom_prefix = f"[{mod_name}/{record.funcName}]"
        return super().format(record)

handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter('%(custom_prefix)s %(message)s'))
logging.basicConfig(level=logging.INFO, handlers=[handler])

# Ensure media directory exists
os.makedirs("media", exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json"
)

# Required by Authlib for Starlette
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)  # ✅ Required by Authlib for Google OAuth state/nonce

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # ⚠️ See note below
    allow_credentials=True,  # ✅ Critical — allows cookies to be sent cross-origin
    allow_methods=["*"],     # ✅ Fine
    allow_headers=["*"],     # ✅ Fine
)


app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI Template. Visit /docs for the API documentation."}
