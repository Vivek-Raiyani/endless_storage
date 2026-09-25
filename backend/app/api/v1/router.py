from fastapi import APIRouter
from app.api.v1.routes import auth, assets, users

api_router = APIRouter()

# Auth Endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Profile Endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Assests Endpoints
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])