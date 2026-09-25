from sqlalchemy import Boolean, Column, String
from app.models.base import Base, SoftDeleteMixin

class User(SoftDeleteMixin, Base):
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  
    google_id = Column(String, unique=True, index=True, nullable=True)
    auth_provider = Column(String, default="local", nullable=False)
    age_consent = Column(Boolean, default=False, nullable=False)
    terms_policy_accepted = Column(Boolean, default=False, nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
