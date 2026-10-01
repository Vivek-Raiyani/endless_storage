from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateOAuth
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    logger.info(f"Fetching user by email: {email}")
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    import uuid
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None
    result = await db.execute(select(User).filter(User.id == uid))
    return result.scalars().first()

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    logger.info(f"Creating new local user: {user_in.email}")
    db_obj = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=get_password_hash(user_in.password),
        age_consent=user_in.age_consent,
        terms_policy_accepted=user_in.terms_policy_accepted,
        is_active=True,
        is_superuser=False,
        auth_provider="local"
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def create_or_get_oauth_user(db: AsyncSession, user_in: UserCreateOAuth) -> User:
    logger.info(f"Processing OAuth user: {user_in.email}")
    user = await get_user_by_email(db, email=user_in.email)
    if user:
        if not user.google_id:
            user.google_id = user_in.google_id
            user.auth_provider = "google"
            await db.commit()
            await db.refresh(user)
        return user
    
    db_obj = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        google_id=user_in.google_id,
        auth_provider=user_in.auth_provider,
        age_consent=user_in.age_consent,
        terms_policy_accepted=user_in.terms_policy_accepted,
        is_active=True,
        is_superuser=False
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
