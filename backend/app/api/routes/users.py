from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.response import DataResponse, MessageResponse
from app.schemas.user import UserOut, UserUpdate, UserUpdatePassword
from app.services.user_service import user_service
from app.core.security import verify_password, get_password_hash
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/profile", response_model=DataResponse[UserOut])
async def get_profile(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    logger.info(f"Fetching profile for user {current_user.id}")
    return DataResponse(data=current_user)

@router.patch("/profile", response_model=DataResponse[UserOut])
async def update_profile(
    user_in: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    logger.info(f"Updating profile for user {current_user.id}")
    if user_in.email and user_in.email != current_user.email:
        existing_user = await user_service.get_user_by_email(db, user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already taken")
            
    updated_user = await user_service.update_user(db, current_user, user_in)
    return DataResponse(data=updated_user)

@router.post("/update-password", response_model=MessageResponse)
async def update_password(
    password_in: UserUpdatePassword,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if not current_user.hashed_password:
        raise HTTPException(status_code=400, detail="User authenticated via OAuth does not have a password. Please use OAuth to login.")
        
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    current_user.hashed_password = get_password_hash(password_in.new_password)
    await db.commit()
    
    return MessageResponse(message="Password updated successfully")
