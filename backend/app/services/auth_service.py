from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateOAuth
from app.core.security import get_password_hash

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, data: UserCreate) -> User:
    db_obj = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        hashed_password=get_password_hash(data.password),
        age_consent=data.age_consent,
        terms_policy_accepted=data.terms_policy_accepted,
        is_active=True,
        is_superuser=False,
        auth_provider="local"
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def create_or_get_oauth_user(db: AsyncSession, data: UserCreateOAuth) -> User:
    user = await get_user_by_email(db, email=data.email)
    if user:
        if not user.google_id:
            user.google_id = data.google_id
            user.auth_provider = "google"
            await db.commit()
            await db.refresh(user)
        return user
    
    db_obj = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        google_id=data.google_id,
        auth_provider=data.auth_provider,
        age_consent=data.age_consent,
        terms_policy_accepted=data.terms_policy_accepted,
        is_active=True,
        is_superuser=False
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
