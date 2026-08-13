from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
import enum
from database.session import Base
from models.base import TimestampMixin, BaseIDMixin

class UserRole(str,enum.Enum):
    ADMIN ="admin"
    RESTAURANT="restaurant"
    CUSTOMER = "customer"
    DELIVERY_PARTNER="delivery_partner"

class User(Base,BaseIDMixin,TimestampMixin):
    __tablename__="users"

    email=Column(String,unique=True , index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    full_name=Column(String,nullable=False)
    phone_number=Column(String,unique=True,nullable=True,index=True)
    is_active=Column(Boolean,default=True)
    is_verified=Column(Boolean,default=True)
    role=Column(SqlEnum(UserRole),default=UserRole.CUSTOMER)

  #  refresh_tokens=relationship("refreshToken",back_populates="user",cascade="all,delete-orphan")

# class refreshTokens(Base,BaseIDMixin,TimestampMixin):
#     __tablename_="refresh_tokens"

#     token=Column(String,unique=True,index=True,nullable=False)
#     user_id=Column(Integer,ForeignKey("users_id"),nullable=False)
#     expires_at=Column(DateTime,nullable=False)
#     is_revoked=Column(Boolean,default=False)
#     user=relationship("user",back_populates="refresh_tokens")