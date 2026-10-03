from fastapi import APIRouter
from app.api.routes import auth, users, storage_accounts, files, folders

api_router = APIRouter()

# Auth Endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Profile Endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Endless Storage — Storage Accounts (connect Google Drive)
api_router.include_router(storage_accounts.router, prefix="/storage-accounts", tags=["storage-accounts"])

# Endless Storage — Virtual Files (upload / download / manage)
api_router.include_router(files.router, prefix="/files", tags=["files"])

# Endless Storage — Virtual Folders (hierarchy)
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
