from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    first_name: str
    last_name: str | None = None
    password: str
    age_consent: bool
    terms_policy_accepted: bool

class UserCreateOAuth(UserBase):
    first_name: str
    last_name: str | None = None
    google_id: str | None = None
    auth_provider: str
    age_consent: bool = False
    terms_policy_accepted: bool = False

class UserLogin(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str

class UserOut(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        from_attributes = True
