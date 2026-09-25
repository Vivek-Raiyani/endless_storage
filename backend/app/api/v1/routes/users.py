from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User
from app.schemas.response import DataResponse, MessageResponse
from app.schemas.user import UserOut, UserUpdate, UserUpdatePassword
from app.services.user_service import user_service
from app.core.security import verify_password, get_password_hash

router = APIRouter()

@router.patch("/me", response_model=DataResponse[UserOut])
async def update_me(
    payload: UserUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if payload.email and payload.email != current_user.email:
        raise HTTPException(status_code=403, detail="Can't Update Others Profile!")
    
    existing_user = await user_service.get_user_by_email(db, payload.email)
    if not existing_user.is_active:
        raise HTTPException(status_code=400, detail="Account is Inactive, Contact support.")
            
    updated_user = await user_service.update_user(db, current_user, payload)
    return DataResponse(data=updated_user)

@router.post("/update-password", response_model=MessageResponse)
async def update_password(
    payload: UserUpdatePassword,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if not current_user.hashed_password and current_user.auth_provider == 'google':
        raise HTTPException(status_code=400, detail="User authenticated via OAuth does not have a password. Please use OAuth to login.")
        
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
        
    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()
    
    return MessageResponse(message="Password updated successfully")
