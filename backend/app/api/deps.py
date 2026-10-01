from typing import AsyncGenerator
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError
import uuid
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User

from app.schemas.token import TokenPayload

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db

def _extract_token_from_cookie(request: Request) -> str:
    """Extract and validate the raw JWT string from the access_token cookie."""
    cookie_value = request.cookies.get("access_token")
    if not cookie_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    # Cookie is stored as "Bearer <token>"
    if not cookie_value.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )
    return cookie_value[len("Bearer "):]

async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    logger.info("Authenticating user via cookie")
    token = _extract_token_from_cookie(request)
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    try:
        user_uuid = uuid.UUID(token_data.sub)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token subject format")

    result = await db.execute(select(User).filter(User.id == user_uuid))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
